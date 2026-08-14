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

from scipion.install.funcs import InstallHelper

from pwchem import Plugin as pwchemPlugin

from .constants import DEEPMVP_DIC, MODEL_DOWNLOAD_URL, NOINSTALL_WARNING, UPSTREAM_URL

_references = []  # DeepMVP does not have a formal citable publication yet (repo/README verified, no own bibtex).


class Plugin(pwchemPlugin):
    """DeepMVP (bzhanglab/DeepMVP, GPL-3.0) is installed by cloning the
    upstream repo and building a dedicated conda environment with its real
    dependency stack (TensorFlow 2.4.2, Python 3.7.10 -- see the real repo's
    environment.yml). The pretrained WEIGHTS are NOT installed
    automatically: http://DeepMVP.ptmax.org/ is a Shiny app (confirmed via
    curl, not a direct file link), so there is no real way to script that
    download -- the same kind of manual step as scipion-chem-netmhcpan's
    NetMHCpan/NetMHCIIpan weights (although here there is no license
    restriction, only the technical impossibility of automating the
    download).
    DEEPMVP_MODEL_DIR must point, after the manual download+decompression,
    to the folder containing the 8 residue-specific model subfolders. See
    README.rst for the full step-by-step."""

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(DEEPMVP_DIC['home'], cls.getEnvName(DEEPMVP_DIC))
        cls._defineVar(DEEPMVP_DIC['activation'], cls.getEnvActivationCommand(DEEPMVP_DIC))
        # Empty by default (same pattern as scipion-chem-netmhcpan's
        # NETMHCPAN_HOME): the user must point it to the weights folder
        # after the manual download, there is no valid default path
        # possible.
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
        installer.addCommand(
            f"git clone --depth 1 {UPSTREAM_URL} {home}",
            'DEEPMVP_CLONED'
        ).getCondaEnvCommand(
            DEEPMVP_DIC['name'], binaryVersion=DEEPMVP_DIC['version'], pythonVersion='3.7'
        ).addCommand(
            f"{cls.getEnvActivationCommand(DEEPMVP_DIC)} && "
            f"cd {home} && pip install -r requirements.txt",
            'DEEPMVP_INSTALLED'
        ).addPackage(env, dependencies=['conda', 'git'], default=default)

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
                f"DEEPMVP_MODEL_DIR ('{modelDir}') is empty or not set -- download the pretrained "
                f"weights manually from {MODEL_DOWNLOAD_URL} (a Shiny app, not a direct-download "
                "link -- cannot be scripted), decompress the .tar.gz, and point DEEPMVP_MODEL_DIR "
                "at the resulting folder (must contain the 8 residue-specific model subfolders)."
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
        return cls.getVar(DEEPMVP_DIC['model_dir'])

    # ---------------------------------- Protocol functions-----------------------

    @classmethod
    def runDeepMVP(cls, protocol, args, cwd=None):
        activation = cls.getVar(DEEPMVP_DIC['activation'])
        scriptPath = cls.getDeepMVPScriptPath()
        # MPLBACKEND=Agg: would otherwise be inherited from the parent
        # process, and an interactive/inline backend does not exist in the
        # isolated conda environment.
        fullProgram = f'MPLBACKEND=Agg {activation} && python {scriptPath}'
        protocol.runJob(fullProgram, args, env=cls.getEnviron(), cwd=cwd)
