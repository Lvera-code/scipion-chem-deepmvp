# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     Enzo Sierra (enzogael57@gmail.com)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************
"""
This protocol predicts post-translational modification (PTM) sites on a
protein sequence using a local DeepMVP installation.
"""

import os

from pwchem.objects import Sequence, SequenceROI, SetOfSequenceROIs
from pwem.protocols import EMProtocol
from pyworkflow.object import Boolean, Float, String
from pyworkflow.protocol import params

from .. import Plugin as deepmvpPlugin
from ..constants import DEFAULT_MAX_FPR
from ..utils.parse_output import parse_site_predictions


class ProtDeepMVPPrediction(EMProtocol):
    """
    Predicts PTM candidate sites (acetylation, N-glycosylation,
    methylation, phosphorylation, sumoylation, ubiquitination -- 8
    residue-specific models covering 6 biological categories, see
    DeepMVP's own README) directly from a protein sequence, using a local
    DeepMVP (bzhanglab/DeepMVP) installation. No structure needed -- this
    is the sole PTM-site engine of the FASTA-only path of the standalone
    PTM-Prediction pipeline (``pipeline.py::run_fase2_fasta_motor``), and
    one of two engines (together with DeepPTMPred) that a downstream
    ``scipion-chem-ptmannotation`` protocol fuses into consensus when a
    structure is also available.

    DeepMVP reports a raw prediction score (``y_pred``) AND a calibrated
    false-positive-rate estimate (``fpr``, generated per-model against
    each model's own calibration set -- see DeepMVP's README): this
    protocol's own ``maxFpr`` threshold decides ``_passesThreshold``, but
    BOTH scores are always kept on the output ROI, unfiltered, so a
    downstream consensus protocol can apply its own criteria without
    having to re-run DeepMVP.

    Output
    ------
    outputROIs: SetOfSequenceROIs, one SequenceROI per candidate site
    (single-residue ROI, ``roiIdx == roiIdx2`` -- a PTM site is a point on
    the sequence, not a span). Each ROI carries ``_type`` (PTM type, DeepMVP's
    own residue-specific model name, e.g. ``'acetylation_k'``),
    ``_scoreDeepmvp`` (raw ``y_pred``), ``_fpr`` (calibrated false-positive
    rate) and ``_passesThreshold`` (``fpr <= maxFpr``).
    """

    _label = 'deepmvp ptm prediction'

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputSequence', params.PointerParam, pointerClass='Sequence',
                       label='Input sequence: ',
                       help='Protein sequence to scan for PTM candidate sites.')
        form.addParam('maxFpr', params.FloatParam, default=DEFAULT_MAX_FPR,
                       label='Max. false-positive rate: ',
                       help="Site-level threshold on DeepMVP's own calibrated 'fpr' column "
                            "(NOT the raw 'y_pred' score -- DeepMVP calibrates a separate "
                            "false-positive-rate estimate per model). A site passes if "
                            "fpr <= this value. Both scores are always kept on the output ROI "
                            'regardless of this threshold.')
        form.addParam('timeoutSeconds', params.IntParam, default=1800,
                       label='Timeout (s): ', expertLevel=params.LEVEL_ADVANCED,
                       help='Maximum time DeepMVP is allowed to run before the step is aborted '
                            'as failed. Increase on slow/CPU-only hardware or long sequences.')

    def _insertAllSteps(self):
        self._insertFunctionStep(self.deepmvpStep)
        self._insertFunctionStep(self.createOutputStep)

    # ---------------------------------- Steps -----------------------------------

    def deepmvpStep(self):
        inpSeq = self.inputSequence.get()
        faFile = self._getExtraPath('inputSequence.fa')
        inpSeq.exportToFile(faFile)

        # ABSOLUTE paths are mandatory: the subprocess runs with
        # cwd=DeepMVP_HOME (see runDeepMVP below), so a relative path from
        # self._getExtraPath() (relative to the Scipion project root) would
        # resolve against the wrong cwd -- same pattern already documented
        # in scipion-chem-netcleave (protocol_netcleave.py).
        faFileAbs = os.path.abspath(faFile)
        resultDirAbs = os.path.abspath(self._getExtraPath('deepmvp_out'))

        args = (
            f'predict -m {deepmvpPlugin.getModelDir()} -d {faFileAbs} -t 2 -o {resultDirAbs}'
        )
        deepmvpPlugin.runDeepMVP(self, args, cwd=deepmvpPlugin.getDeepMVPDir())

    def createOutputStep(self):
        inpSeq = self.inputSequence.get()
        resultDir = self._getExtraPath('deepmvp_out')
        rows = parse_site_predictions(resultDir)

        outROIs = SetOfSequenceROIs(filename=self._getPath('sequenceROIs.sqlite'))
        maxFpr = self.maxFpr.get()
        for row in rows:
            pos = int(row['pos'])
            residue = row['aa']
            idxs = [pos, pos]
            roiSeq = Sequence(sequence=residue, name=f'ROI_{pos}', id=f'ROI_{pos}',
                               description=f"DeepMVP {row['ptm']} candidate")
            seqROI = SequenceROI(sequence=inpSeq, seqROI=roiSeq, roiIdx=idxs[0], roiIdx2=idxs[1])
            seqROI.setType(row['ptm'])
            seqROI._scoreDeepmvp = Float(float(row['y_pred']))
            seqROI._fpr = Float(float(row['fpr']))
            seqROI._passesThreshold = Boolean(float(row['fpr']) <= maxFpr)
            seqROI._residueWt = String(residue)
            # Project-wide convention (see
            # scipion-chem-epitope-construct/.../protocol_epitope_construct.py:66-75):
            # any prediction protocol must expose '_meanScore' so that generic
            # ranking/consensus protocols (e.g. a future
            # ProtCombineScoresSeqROI) can order results without knowing the
            # specific name of each engine. y_pred (not 'fpr', which is a
            # threshold, not a confidence score) is the real confidence
            # metric here.
            seqROI._meanScore = Float(float(row['y_pred']))
            outROIs.append(seqROI)

        if len(outROIs) > 0:
            self._defineOutputs(outputROIs=outROIs)
            self._defineSourceRelation(self.inputSequence, outROIs)

    # ---------------------------------- Validation -------------------------------

    def _validate(self):
        return deepmvpPlugin.validateInstallation()

    def _summary(self):
        summary = []
        if self.isFinished():
            outROIs = getattr(self, 'outputROIs', None)
            if outROIs is not None:
                nPass = sum(1 for roi in outROIs if roi._passesThreshold.get())
                summary.append(f'{nPass}/{len(outROIs)} candidate site(s) pass the fpr threshold.')
        return summary
