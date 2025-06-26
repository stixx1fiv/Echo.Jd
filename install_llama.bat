@echo off
set CMAKE_ARGS=-DGGML_CUDA=on
set FORCE_CMAKE=1
pip uninstall -y llama-cpp-python
pip install --no-cache-dir --verbose llama-cpp-python 