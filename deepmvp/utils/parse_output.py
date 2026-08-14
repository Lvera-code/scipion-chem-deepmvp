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
Parsing of 'site_prediction.tsv' (real DeepMVP output in 'predict -t 2'
mode, prefix hardcoded in the upstream repo -- see constants.py). Each
plugin in this project keeps its own minimal copy of this kind of parsing
logic (same policy as StackGlyEmbed/NetCleave) rather than a shared
dependency.
"""

import csv
import os

from ..constants import OUTPUT_COLUMNS, SITE_PREDICTION_FILENAME


class DeepMVPOutputError(Exception):
    pass


def parse_site_predictions(resultDir):
    """Reads '<resultDir>/site_prediction.tsv' and returns a list of dicts
    with OUTPUT_COLUMNS (protein/aa/pos/x/y_pred/fpr/ptm), one entry per
    candidate PTM site reported by DeepMVP.

    Raises:
        DeepMVPOutputError: if the file does not exist or is missing
            expected columns (e.g. a newer DeepMVP version changed its
            output format).
    """
    tsvPath = os.path.join(resultDir, SITE_PREDICTION_FILENAME)
    if not os.path.isfile(tsvPath):
        raise DeepMVPOutputError(
            f"DeepMVP did not generate '{SITE_PREDICTION_FILENAME}' in '{resultDir}'. The subprocess "
            "reported exit code 0 but the expected output file does not exist."
        )

    with open(tsvPath, newline='') as fh:
        reader = csv.DictReader(fh, delimiter='\t')
        missing = [c for c in OUTPUT_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise DeepMVPOutputError(
                f"'{tsvPath}' does not have the expected columns {OUTPUT_COLUMNS} (missing: {missing}, "
                f"actual columns: {reader.fieldnames}). A newer DeepMVP version may have "
                "changed its output format."
            )
        return [{col: row[col] for col in OUTPUT_COLUMNS} for row in reader]
