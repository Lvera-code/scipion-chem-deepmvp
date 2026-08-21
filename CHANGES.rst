=========
CHANGES
=========

0.3.0
=====
- Pretrained weights are now auto-downloaded and extracted at install time
  (the Shiny app's download button has a real direct file URL behind it)
  into ``<DEEPMVP_HOME>/modelFiles/models`` -- no manual download/
  ``scipion.conf`` entry needed anymore. Removed unused ``READ_URL``
  constant.

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
  same one-plugin-per-tool pattern used across this project's other
  plugins. No installation or protocol logic yet.
