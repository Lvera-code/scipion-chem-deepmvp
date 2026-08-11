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

_references = []  # DeepMVP no tiene una publicacion formal citable todavia (repo/README verificados, sin bibtex propio).


class Plugin(pwchemPlugin):
    """DeepMVP (bzhanglab/DeepMVP, GPL-3.0) se instala clonando el repo
    upstream y construyendo un entorno conda dedicado con su stack de
    dependencias real (TensorFlow 2.4.2, Python 3.7.10 -- ver
    environment.yml del repo real). Los PESOS pre-entrenados NO se instalan
    automaticamente: http://DeepMVP.ptmax.org/ es una app Shiny (confirmado
    via curl, no un enlace directo a archivo), asi que no hay forma real de
    scriptear esa descarga -- mismo tipo de paso manual que NetMHCpan/
    NetMHCIIpan en el proyecto 1 (aunque aqui no hay restriccion de
    licencia, solo imposibilidad tecnica de automatizar la descarga).
    DEEPMVP_MODEL_DIR debe apuntar, tras la descarga+descompresion manual, a
    la carpeta que contiene las 8 subcarpetas de modelo especificas de
    residuo. Ver README.rst para el paso a paso completo."""

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(DEEPMVP_DIC['home'], cls.getEnvName(DEEPMVP_DIC))
        cls._defineVar(DEEPMVP_DIC['activation'], cls.getEnvActivationCommand(DEEPMVP_DIC))
        # Vacio por defecto (mismo patron que NETMHCPAN_HOME en el proyecto
        # 1): el usuario debe apuntarlo a la carpeta de pesos tras la
        # descarga manual, no hay una ruta por defecto valida posible.
        cls._defineVar(DEEPMVP_DIC['model_dir'], '')

    @classmethod
    def defineBinaries(cls, env):
        cls.addDeepMVPPackage(env)

    @classmethod
    def addDeepMVPPackage(cls, env, default=True):
        home = cls.getVar(DEEPMVP_DIC['home'])

        installer = InstallHelper(DEEPMVP_DIC['name'], packageHome=home,
                                  packageVersion=DEEPMVP_DIC['version'])

        # requirements.txt (verificado contra el archivo real del repo
        # upstream) se usa tal cual, sin parchear -- a diferencia de
        # StackGlyEmbed, este es el archivo de PREDICCION real (no uno de
        # entrenamiento con pines invalidos), y sus 7 lineas
        # (tensorflow==2.4.2, pandas, scikit-learn, matplotlib, biopython,
        # pyteomics, shap==0.39.0) son exactamente lo que DeepMVP.py importa
        # en el camino de prediccion (verificado leyendo lib/PTModels.py).
        #
        # Clone ANTES de crear el entorno conda (mismo bug real ya
        # encontrado+corregido en netcleave/iapred/scannet/discotope/
        # stackglyembed en el proyecto 1, ver netcleave/__init__.py:
        # 'InstallHelper.addCommand' -- y por tanto 'getCondaEnvCommand',
        # que lo usa internamente -- deja su propio marcador de finalizacion
        # DENTRO de 'packageHome'; crear el entorno antes de clonar deja ese
        # marcador en 'home' y bloquea el 'git clone' posterior, que exige
        # un destino vacio o inexistente).
        #
        # pythonVersion='3.7' (no la version por defecto del resto de
        # plugins de este proyecto): TensorFlow 2.4.2 exige Python<=3.8,
        # confirmado en environment.yml del repo real ('python=3.7.10').
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
        # MPLBACKEND=Agg (mismo motivo real documentado en
        # PTM-Prediction/src/engines/deepmvp_engine.py): MPLBACKEND se
        # heredaria del proceso padre si no se fuerza aqui, y un backend
        # interactivo/inline no existe en el entorno conda aislado.
        fullProgram = f'MPLBACKEND=Agg {activation} && python {scriptPath}'
        protocol.runJob(fullProgram, args, env=cls.getEnviron(), cwd=cwd)
