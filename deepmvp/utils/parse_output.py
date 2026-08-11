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
Parseo de 'site_prediction.tsv' (salida real de DeepMVP en modo 'predict
-t 2', prefix hardcodeado en el repo upstream -- ver constants.py). Logica
vendorizada de forma independiente (misma politica que StackGlyEmbed/
NetCleave en el proyecto 1: este plugin no importa el proyecto hermano
PTM-Prediction, cada uno mantiene su propia copia minima de lo que
necesita) a partir del mismo contrato ya validado end-to-end en
PTM-Prediction/src/engines/deepmvp_engine.py.
"""

import csv
import os

from ..constants import OUTPUT_COLUMNS, SITE_PREDICTION_FILENAME


class DeepMVPOutputError(Exception):
    pass


def parse_site_predictions(resultDir):
    """Lee '<resultDir>/site_prediction.tsv' y devuelve una lista de dicts
    con OUTPUT_COLUMNS (protein/aa/pos/x/y_pred/fpr/ptm), una entrada por
    sitio PTM candidato reportado por DeepMVP.

    Raises:
        DeepMVPOutputError: si el archivo no existe o le faltan columnas
            esperadas (p.ej. una version mas nueva de DeepMVP cambio su
            formato de salida).
    """
    tsvPath = os.path.join(resultDir, SITE_PREDICTION_FILENAME)
    if not os.path.isfile(tsvPath):
        raise DeepMVPOutputError(
            f"DeepMVP no genero '{SITE_PREDICTION_FILENAME}' en '{resultDir}'. El subproceso "
            "reporto exit code 0 pero el archivo de salida esperado no existe."
        )

    with open(tsvPath, newline='') as fh:
        reader = csv.DictReader(fh, delimiter='\t')
        missing = [c for c in OUTPUT_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise DeepMVPOutputError(
                f"'{tsvPath}' no tiene las columnas esperadas {OUTPUT_COLUMNS} (faltan: {missing}, "
                f"columnas reales: {reader.fieldnames}). Puede que una version mas nueva de DeepMVP "
                "haya cambiado su formato de salida."
            )
        return [{col: row[col] for col in OUTPUT_COLUMNS} for row in reader]
