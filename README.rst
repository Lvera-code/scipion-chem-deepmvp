================================
DeepMVP Scipion plugin
================================

Scipion framework plugin wrapping DeepMVP (Nature Methods, 2025) --
core PTM prediction engine (FASTA path, 6 types), with optional consensus
with DeepPTMPred on the PDB path.

``ProtDeepMVPPrediction`` wraps a local DeepMVP installation directly, no
vendored/reimplemented prediction logic.

Original repo: https://github.com/bzhanglab/DeepMVP

Citation: doi.org/10.1038/s41592-025-02797-x

**DeepMVP license (upstream)**: GPL-3.0, declared in the LICENSE of the original repo (bzhanglab/DeepMVP) -- verified against the actual file, not assumed.

===================
Install this plugin
===================

**Developer's version**

.. code-block::

            git clone https://github.com/Lvera-code/scipion-chem-deepmvp.git
            cd scipion-chem-deepmvp
            scipion3 installp -p . --devel
            scipion3 installb DeepMVP

The repo and the conda environment (Python 3.7.10, TensorFlow 2.4.2) are
installed automatically. The **pretrained weights are NOT** -- ``http://DeepMVP.ptmax.org/``
is a Shiny app, not a direct-download link, so it cannot be scripted.
Download them manually, decompress the ``.tar.gz``, and point
``DEEPMVP_MODEL_DIR`` (in ``scipion.conf``) to the resulting folder (it must
contain the 8 model subfolders: ``acetylation_k``, ``glycosylation_n``,
``methylation_k``, ``methylation_r``, ``phosphorylation_st``,
``phosphorylation_y``, ``sumoylation_k``, ``ubiquitination_k``).

.. code-block::

            scipion3 tests deepmvp.tests
