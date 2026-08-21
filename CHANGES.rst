=========
CHANGES
=========

0.4.1
=====
- Fixed two real bugs in the GPU install branch found via an actual
  end-to-end fresh install + real prediction on a real GPU machine: (1)
  ``cudatoolkit``/``cudnn`` are not available in the ``defaults`` channel
  at all (added ``-c conda-forge``); (2) ``cudnn=8.0.4`` does not exist as
  a real build in any channel (the real closest match is ``8.0.5``).
  Verified after the fix: TensorFlow correctly loads
  ``libcudart.so.11.0``/``libcudnn.so.8`` and detects the real GPU, and a
  real DeepMVP prediction ran successfully end-to-end on GPU.

0.4.0
=====
- GPU support: ``USE_GPU``/``GPU_LIST`` hidden params added to
  ``ProtDeepMVPPrediction`` (same convention as scipion-chem-tmbed/
  -discotope), wired to ``CUDA_VISIBLE_DEVICES`` in ``runDeepMVP`` (no
  native CLI flag exists in DeepMVP.py -- TensorFlow decides GPU/CPU on
  its own, this is the real lever on that decision). Install now also
  installs ``cudatoolkit=11.0``/``cudnn=8.0.4`` (TF 2.4.2's own documented
  compatible pair) when a GPU is detected at install time -- unchanged
  (no-op) on a machine with none. The ``CUDA_VISIBLE_DEVICES`` lever
  itself was verified for real against TensorFlow on a real GPU machine:
  hides/exposes the GPU exactly as expected.

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
