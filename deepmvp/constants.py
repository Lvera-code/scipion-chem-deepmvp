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

UPSTREAM_URL = 'https://github.com/bzhanglab/DeepMVP'

# Confirmed by reading DeepMVP.py ('predict' mode, line ~117-138): it does
# not expose any GPU/device flag -- unlike 'train' mode (line ~40,
# '-gpu'/'--gpu_n'), which this plugin does not use. TensorFlow decides
# CPU/GPU on its own based on what it detects available -- the protocol's
# USE_GPU/GPU_LIST hidden params (see protocol_deepmvp.py) act on that
# decision indirectly, via CUDA_VISIBLE_DEVICES (see runDeepMVP in
# __init__.py), not a real CLI flag (same criterion applied to
# scipion-chem-netcleave/-iapred/-scannet, whose real CLIs also have no
# GPU flag).
GPU_REQUIRED = False

# DeepMVP license (upstream): GPL-3.0, declared in the LICENSE of the original repo (bzhanglab/DeepMVP) -- verified against the real file, not assumed.

# The Shiny app page (https://deepmvp.ptmax.org/) is not itself a direct
# link, but its download button's real target IS a direct, scriptable
# file (found by inspecting the button element, not by curl'ing the page
# itself -- confirmed with 'curl -sIL': 301 to the https URL below, then
# 200, 'content-type: application/gzip', ~1.5GB). Installed automatically
# now (see addDeepMVPPackage in __init__.py) into a 'modelFiles/' folder
# created at install time; DEEPMVP_MODEL_DIR defaults to
# '<DEEPMVP_HOME>/modelFiles/models' (the real top-level folder inside the
# tarball, confirmed via 'tar tzf', containing the 8 model subfolders:
# acetylation_k, glycosylation_n, methylation_k, methylation_r,
# phosphorylation_st, phosphorylation_y, sumoylation_k, ubiquitination_k).
# Still overridable via scipion.conf if a user wants to point elsewhere.
MODEL_DOWNLOAD_URL = 'https://deepmvp.ptmax.org/download/models.tar.gz'

# Real columns of 'site_prediction.tsv' (fixed filename, confirmed by
# reading lib/PTModels.py::ptm_prediction_for_multiple_ptms in the real
# repo -- prefix hardcoded to 'site_prediction'), not guessed.
SITE_PREDICTION_FILENAME = 'site_prediction.tsv'
OUTPUT_COLUMNS = ['protein', 'aa', 'pos', 'x', 'y_pred', 'fpr', 'ptm']

DEFAULT_MAX_FPR = 0.05

NOINSTALL_WARNING = (
    "DeepMVP is not installed correctly. Check that the repo has been cloned "
    "(DEEPMVP_HOME) and that DEEPMVP_MODEL_DIR points to a folder with the "
    f"pretrained weights (auto-downloaded from {MODEL_DOWNLOAD_URL} at install "
    "time into '<DEEPMVP_HOME>/modelFiles/models' -- re-run 'scipion3 installb "
    "deepmvp' if that download failed). See README.rst - Installation."
)
