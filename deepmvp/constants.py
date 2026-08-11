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

# Confirmado leyendo DeepMVP.py (modo 'predict', linea ~117-138): no expone
# ningun flag de GPU/device -- a diferencia del modo 'train' (linea ~40,
# '-gpu'/'--gpu_n'), que este plugin no usa. TensorFlow decide CPU/GPU por
# si solo segun lo que detecte disponible; no hay ningun toggle real que
# exponer en el protocolo (mismo criterio aplicado en el proyecto 1 a
# NetCleave/IApred/ScanNet, cuyos CLIs reales tampoco tienen flag de GPU).
GPU_REQUIRED = False

# Licencia de DeepMVP (upstream): GPL-3.0, declarada en el LICENSE del repo original (bzhanglab/DeepMVP) -- verificada contra el archivo real, no asumida.

# Los pesos pre-entrenados NO se pueden descargar de forma automatizable:
# http://DeepMVP.ptmax.org/ es una app Shiny (confirmado via 'curl -sIL',
# 'X-Powered-By: Shiny Server'), no un enlace directo a un .tar.gz -- mismo
# tipo de bloqueo real que motivo el patron de instalacion manual de
# NetMHCpan/NetMHCIIpan en el proyecto 1 (aunque aqui no hay licencia
# academica de por medio, solo imposibilidad de scriptear la descarga).
# DEEPMVP_MODEL_DIR debe apuntar, tras la descarga+descompresion manual, a
# la carpeta con las 8 subcarpetas de modelo (acetylation_k,
# glycosylation_n, methylation_k, methylation_r, phosphorylation_st,
# phosphorylation_y, sumoylation_k, ubiquitination_k) -- ver README.rst.
MODEL_DOWNLOAD_URL = 'https://deepmvp.ptmax.org/'

# Columnas reales de 'site_prediction.tsv' (nombre de archivo fijo,
# confirmado leyendo lib/PTModels.py::ptm_prediction_for_multiple_ptms del
# repo real -- prefix hardcodeado a 'site_prediction'). Verificado tambien
# contra PTM-Prediction/src/engines/deepmvp_engine.py::OUTPUT_COLUMNS (motor
# ya validado end-to-end en el pipeline standalone), no vuelto a adivinar.
SITE_PREDICTION_FILENAME = 'site_prediction.tsv'
OUTPUT_COLUMNS = ['protein', 'aa', 'pos', 'x', 'y_pred', 'fpr', 'ptm']

DEFAULT_MAX_FPR = 0.05

NOINSTALL_WARNING = (
    "DeepMVP no esta instalado correctamente. Revisa que el repo se haya clonado "
    "(DEEPMVP_HOME) y que DEEPMVP_MODEL_DIR apunte a una carpeta con los pesos "
    f"pre-entrenados, descargados manualmente desde {MODEL_DOWNLOAD_URL} (no "
    "automatizable: es una app Shiny, no un enlace directo). Ver README.rst - "
    "Instalacion."
)
