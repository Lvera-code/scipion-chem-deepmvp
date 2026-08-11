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

DEFAULT_VERSION = '1.0'

DEEPMVP_DIC = {
    'name': 'DeepMVP',
    'version': DEFAULT_VERSION,
    'home': 'DEEPMVP_HOME',
    'activation': 'DEEPMVP_ACTIVATION_CMD',
    'model_dir': 'DEEPMVP_MODEL_DIR',
}

READ_URL = 'https://github.com/Lvera-code/scipion-chem-deepmvp'
UPSTREAM_URL = 'https://github.com/bzhanglab/DeepMVP'

# Confirmed by reading DeepMVP.py ('predict' mode, line ~117-138): it does
# not expose any GPU/device flag -- unlike 'train' mode (line ~40,
# '-gpu'/'--gpu_n'), which this plugin does not use. TensorFlow decides
# CPU/GPU on its own based on what it detects available; there is no real
# toggle to expose in the protocol (same criterion applied in project 1 to
# NetCleave/IApred/ScanNet, whose real CLIs also have no GPU flag).
GPU_REQUIRED = False

# DeepMVP license (upstream): GPL-3.0, declared in the LICENSE of the original repo (bzhanglab/DeepMVP) -- verified against the real file, not assumed.

# The pretrained weights CANNOT be downloaded in a scriptable way:
# http://DeepMVP.ptmax.org/ is a Shiny app (confirmed via 'curl -sIL',
# 'X-Powered-By: Shiny Server'), not a direct link to a .tar.gz -- the same
# kind of real blocker that motivated the manual-installation pattern for
# NetMHCpan/NetMHCIIpan in project 1 (although there is no academic license
# involved here, only the impossibility of scripting the download).
# DEEPMVP_MODEL_DIR must point, after the manual download+decompression, to
# the folder with the 8 model subfolders (acetylation_k, glycosylation_n,
# methylation_k, methylation_r, phosphorylation_st, phosphorylation_y,
# sumoylation_k, ubiquitination_k) -- see README.rst.
MODEL_DOWNLOAD_URL = 'https://deepmvp.ptmax.org/'

# Real columns of 'site_prediction.tsv' (fixed filename, confirmed by
# reading lib/PTModels.py::ptm_prediction_for_multiple_ptms in the real
# repo -- prefix hardcoded to 'site_prediction'). Also verified against
# PTM-Prediction/src/engines/deepmvp_engine.py::OUTPUT_COLUMNS (an engine
# already validated end-to-end in the standalone pipeline), not guessed
# again.
SITE_PREDICTION_FILENAME = 'site_prediction.tsv'
OUTPUT_COLUMNS = ['protein', 'aa', 'pos', 'x', 'y_pred', 'fpr', 'ptm']

DEFAULT_MAX_FPR = 0.05

NOINSTALL_WARNING = (
    "DeepMVP is not installed correctly. Check that the repo has been cloned "
    "(DEEPMVP_HOME) and that DEEPMVP_MODEL_DIR points to a folder with the "
    f"pretrained weights, downloaded manually from {MODEL_DOWNLOAD_URL} (not "
    "scriptable: it is a Shiny app, not a direct link). See README.rst - "
    "Installation."
)
