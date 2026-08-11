================================
DeepMVP Scipion plugin
================================

Scipion framework plugin wrapping DeepMVP (Nature Methods, 2025) --
motor central de prediccion de PTM (Camino FASTA, 6 tipos), consenso opcional con DeepPTMPred en Camino PDB.

``ProtDeepMVPPrediction`` porta la logica ya validada end-to-end en el
pipeline standalone (``PTM-Prediction/src/engines/deepmvp_engine.py``).

Repo original: https://github.com/bzhanglab/DeepMVP

Cita: doi.org/10.1038/s41592-025-02797-x

**Licencia de DeepMVP (upstream)**: GPL-3.0, declarada en el LICENSE del repo original (bzhanglab/DeepMVP) -- verificada contra el archivo real, no asumida.

===================
Install this plugin
===================

**Developer's version**

.. code-block::

            git clone https://github.com/Lvera-code/scipion-chem-deepmvp.git
            cd scipion-chem-deepmvp
            scipion3 installp -p . --devel
            scipion3 installb DeepMVP

El repo y el entorno conda (Python 3.7.10, TensorFlow 2.4.2) se instalan
automaticamente. Los **pesos pre-entrenados NO** -- ``http://DeepMVP.ptmax.org/``
es una app Shiny, no un enlace de descarga directa, asi que no se puede
scriptear. Descargalos manualmente, descomprime el ``.tar.gz`` y apunta
``DEEPMVP_MODEL_DIR`` (en ``scipion.conf``) a la carpeta resultante (debe
contener las 8 subcarpetas de modelo: ``acetylation_k``, ``glycosylation_n``,
``methylation_k``, ``methylation_r``, ``phosphorylation_st``,
``phosphorylation_y``, ``sumoylation_k``, ``ubiquitination_k``).

.. code-block::

            scipion3 tests deepmvp.tests
