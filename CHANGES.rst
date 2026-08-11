=========
CHANGES
=========

0.2.0
=====
- Real protocol (``ProtDeepMVPPrediction``): FASTA -> candidate PTM sites
  (one ``SequenceROI`` per site, ``_type``/``_scoreDeepmvp``/``_fpr``/
  ``_passesThreshold``). Automatic installation of the repo+conda
  environment (Python 3.7.10, TensorFlow 2.4.2); manual pretrained weights
  (``DEEPMVP_MODEL_DIR``, download cannot be automated -- Shiny app, no
  direct link). Real test with the example sequence from the upstream
  repo itself (Q5S007/LRRK2).

0.1.0
=====
- Initial scaffolding: Scipion plugin structure generated following the
  same pattern as the BCell-Epitope-Prediction plugins (one plugin per
  tool). No installation or protocol logic yet -- pending end-to-end
  validation of the pipeline on Colab, see STATUS.md of the
  ``PTM-Prediction`` project.
