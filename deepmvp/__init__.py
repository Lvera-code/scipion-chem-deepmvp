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
This package contains a protocol for PTM site prediction using a local
DeepMVP installation.
"""

import os
import subprocess

from pyworkflow.utils import Environ
from scipion.install.funcs import InstallHelper

from pwchem import Plugin as pwchemPlugin

from .constants import DEEPMVP_DIC, MODEL_DOWNLOAD_URL, NOINSTALL_WARNING, UPSTREAM_URL

_references = []  # DeepMVP does not have a formal citable publication yet (repo/README verified, no own bibtex).


class Plugin(pwchemPlugin):
    """DeepMVP (bzhanglab/DeepMVP, GPL-3.0) is installed by cloning the
    upstream repo and building a dedicated conda environment with its real
    dependency stack (TensorFlow 2.4.2, Python 3.7.10 -- see the real repo's
    environment.yml). The pretrained weights are downloaded automatically
    too: although https://deepmvp.ptmax.org/ itself is a Shiny app (not a
    direct file link), its download button's real target IS a direct,
    scriptable file (see MODEL_DOWNLOAD_URL in constants.py), extracted
    into ``<DEEPMVP_HOME>/modelFiles/models``. See README.rst for details."""

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(DEEPMVP_DIC['home'], cls.getEnvName(DEEPMVP_DIC))
        cls._defineVar(DEEPMVP_DIC['activation'], cls.getEnvActivationCommand(DEEPMVP_DIC))
        # Empty by default: 'getModelDir()' below falls back to where
        # addDeepMVPPackage auto-downloads+extracts the weights
        # ('<DEEPMVP_HOME>/modelFiles/models') when this is unset -- still
        # overridable via scipion.conf if a user wants to point elsewhere
        # (e.g. a weights folder shared across machines).
        cls._defineVar(DEEPMVP_DIC['model_dir'], '')

    @classmethod
    def defineBinaries(cls, env):
        cls.addDeepMVPPackage(env)

    @classmethod
    def addDeepMVPPackage(cls, env, default=True):
        home = cls.getVar(DEEPMVP_DIC['home'])

        installer = InstallHelper(DEEPMVP_DIC['name'], packageHome=home,
                                  packageVersion=DEEPMVP_DIC['version'])

        # requirements.txt (verified against the real file in the upstream
        # repo) is used as-is, without patching -- unlike StackGlyEmbed,
        # this is the real PREDICTION file (not a training one with invalid
        # pins), and its 7 lines (tensorflow==2.4.2, pandas, scikit-learn,
        # matplotlib, biopython, pyteomics, shap==0.39.0) are exactly what
        # DeepMVP.py imports on the prediction path (verified by reading
        # lib/PTModels.py).
        #
        # Clone BEFORE creating the conda environment (same pattern applied
        # in netcleave/iapred/scannet/discotope/stackglyembed, see
        # netcleave/__init__.py:
        # 'InstallHelper.addCommand' -- and therefore 'getCondaEnvCommand',
        # which uses it internally -- leaves its own completion marker
        # INSIDE 'packageHome'; creating the environment before cloning
        # would leave that marker in 'home' and block the subsequent
        # 'git clone', which requires an empty or nonexistent destination).
        #
        # pythonVersion='3.7' (not the default version used by the rest of
        # this project's plugins): TensorFlow 2.4.2 requires Python<=3.8,
        # confirmed in the real repo's environment.yml ('python=3.7.10').
        # Weights auto-download: MODEL_DOWNLOAD_URL is the real direct file
        # URL behind the Shiny app's download button (see constants.py),
        # ~1.5GB, extracted into a 'modelFiles/' folder created here so
        # DEEPMVP_MODEL_DIR needs no manual scipion.conf entry (see
        # getModelDir()). '-C {home}/modelFiles' (not the default cwd):
        # the tarball's own top-level entry is 'models/', so the resulting
        # path is '<home>/modelFiles/models', matching MODEL_DOWNLOAD_URL's
        # docstring above.
        installer.addCommand(
            f"git clone --depth 1 {UPSTREAM_URL} {home}",
            'DEEPMVP_CLONED'
        ).getCondaEnvCommand(
            DEEPMVP_DIC['name'], binaryVersion=DEEPMVP_DIC['version'], pythonVersion='3.7'
        ).addCommand(
            # cudatoolkit=11.0/cudnn=8.0.5: TF 2.4.2's own documented
            # compatible CUDA/cuDNN pair (tensorflow.org build config
            # history) -- TF's pip wheel already supports GPU, it just
            # needs these shared libraries findable at runtime. Only
            # installed when a GPU is actually present (checked via
            # 'nvidia-smi').
            # TWO real bugs found+fixed via an actual install run on a
            # real GPU (Colab, Tesla T4, 2026-08-21): (1) neither package
            # exists in the 'defaults' channel at all (real
            # 'PackagesNotFoundInChannelsError') -- '-c conda-forge'
            # added; (2) 'cudnn=8.0.4' does not exist as a real build in
            # ANY channel (confirmed via 'conda search') -- the real
            # closest/matching build is '8.0.5.39', pinned here as
            # '8.0.5'. Both installed successfully together with this fix.
            f"if command -v nvidia-smi > /dev/null 2>&1; then "
            f"{cls.getEnvActivationCommand(DEEPMVP_DIC)} && "
            f"conda install -y -c conda-forge cudatoolkit=11.0 cudnn=8.0.5; fi",
            'DEEPMVP_GPU_LIBS_CHECKED'
        ).addCommand(
            f"{cls.getEnvActivationCommand(DEEPMVP_DIC)} && "
            f"cd {home} && pip install -r requirements.txt",
            'DEEPMVP_INSTALLED'
        ).addCommand(
            f"mkdir -p {home}/modelFiles && "
            f"curl -fsSL -o {home}/modelFiles/models.tar.gz {MODEL_DOWNLOAD_URL} && "
            f"tar -xzf {home}/modelFiles/models.tar.gz -C {home}/modelFiles && "
            f"rm -f {home}/modelFiles/models.tar.gz",
            'DEEPMVP_MODELS_DOWNLOADED'
        ).addPackage(env, dependencies=['conda', 'git', 'curl'], default=default)

    @classmethod
    def validateInstallation(cls):
        """Check that this plugin's requirements are met. Returns a list of
        actionable error messages, empty if the installation is correct."""
        errors = []

        scriptPath = cls.getDeepMVPScriptPath()
        if not os.path.isfile(scriptPath):
            errors.append(f"Could not find DeepMVP.py under DEEPMVP_HOME: '{cls.getVar(DEEPMVP_DIC['home'])}'.")
        elif not cls.checkCallEnv(DEEPMVP_DIC):
            errors.append("Activation of the DeepMVP conda environment failed.")

        modelDir = cls.getModelDir()
        if not modelDir or not os.path.isdir(modelDir) or not any(os.scandir(modelDir)):
            errors.append(
                f"DEEPMVP_MODEL_DIR ('{modelDir}') is empty or not set -- it should have been "
                f"auto-downloaded from {MODEL_DOWNLOAD_URL} at install time. Re-run "
                "'scipion3 installb deepmvp' or, if that keeps failing, download it manually and "
                "point DEEPMVP_MODEL_DIR at the resulting folder (must contain the 8 "
                "residue-specific model subfolders)."
            )

        if errors:
            errors.append(NOINSTALL_WARNING)
        return errors

    @classmethod
    def checkCallEnv(cls, packageDic):
        actCommand = cls.getVar(packageDic['activation'])
        try:
            if 'conda' in actCommand and 'shell.bash hook' not in actCommand:
                actCommand = f'{cls.getCondaActivationCmd()}{actCommand}'
            subprocess.check_output(f'{actCommand} && python -c "import tensorflow"', shell=True)
            return True
        except subprocess.CalledProcessError:
            return False

    # ---------------------------------- Utils -----------------------------------

    @classmethod
    def getDeepMVPDir(cls):
        return cls.getVar(DEEPMVP_DIC['home'])

    @classmethod
    def getDeepMVPScriptPath(cls):
        return os.path.join(cls.getDeepMVPDir(), 'DeepMVP.py')

    @classmethod
    def getModelDir(cls):
        configured = cls.getVar(DEEPMVP_DIC['model_dir'])
        if configured:
            return configured
        # Falls back to where addDeepMVPPackage auto-downloads+extracts the
        # weights when DEEPMVP_MODEL_DIR is unset in scipion.conf.
        return os.path.join(cls.getDeepMVPDir(), 'modelFiles', 'models')

    # ---------------------------------- Protocol functions-----------------------

    @classmethod
    def runDeepMVP(cls, protocol, args, cwd=None):
        activation = cls.getVar(DEEPMVP_DIC['activation'])
        scriptPath = cls.getDeepMVPScriptPath()
        # MPLBACKEND=Agg: would otherwise be inherited from the parent
        # process, and an interactive/inline backend does not exist in the
        # isolated conda environment.
        fullProgram = f'MPLBACKEND=Agg {activation} && python {scriptPath}'
        # CUDA_VISIBLE_DEVICES: DeepMVP.py has no GPU/CPU CLI flag of its
        # own (TF decides based on what it detects) -- this is the actual
        # lever the useGpu/gpuList hidden params (see protocol_deepmvp.py)
        # have on TF's auto-detection. 'cls.getEnviron()' is not used here:
        # it returns None (never overridden anywhere in this project),
        # equivalent to inheriting os.environ unchanged -- building a real
        # copy here is additive, not a behavior change for anything else.
        # Must be a real 'pyworkflow.utils.Environ' (a dict subclass with
        # extra methods like 'getPrepend()' that pyworkflow's own job
        # runner calls) -- a plain dict fails with a real
        # AttributeError, confirmed by an actual failed test run.
        # CUDA_VISIBLE_DEVICES='' vs unset/'0' verified for real against
        # TensorFlow on a real GPU (Colab, Tesla T4, 2026-08-21):
        # 'tf.config.list_physical_devices("GPU")' returns [] when hidden,
        # the real device when not -- this is not just a theoretical lever.
        env = Environ(os.environ)
        env['CUDA_VISIBLE_DEVICES'] = protocol.gpuList.get() if protocol.useGpu.get() else ''
        protocol.runJob(fullProgram, args, env=env, cwd=cwd)
