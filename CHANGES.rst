=========
CHANGES
=========

0.2.0
=====
- Protocolo real (``ProtDeepMVPPrediction``): FASTA -> sitios PTM candidatos
  (una ``SequenceROI`` por sitio, ``_type``/``_scoreDeepmvp``/``_fpr``/
  ``_passesThreshold``). Instalacion automatica del repo+entorno conda
  (Python 3.7.10, TensorFlow 2.4.2); pesos pre-entrenados manuales
  (``DEEPMVP_MODEL_DIR``, descarga no automatizable -- app Shiny, no enlace
  directo). Test real con la secuencia de ejemplo del propio repo upstream
  (Q5S007/LRRK2).

0.1.0
=====
- Scaffolding inicial: estructura de plugin de Scipion generada siguiendo el
  mismo patron que los plugins de BCell-Epitope-Prediction (un plugin por
  herramienta). Sin logica de instalacion ni de protocolo todavia -- pendiente
  de la validacion end-to-end del pipeline en Colab, ver STATUS.md del
  proyecto ``PTM-Prediction``.
