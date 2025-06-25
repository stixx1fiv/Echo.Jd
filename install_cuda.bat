@echo off
pip uninstall -y llama-cpp-python
set CMAKE_ARGS=-DLLAMA_CUBLAS=on
pip install --no-cache-dir --force-reinstall llama-cpp-python --extra-index-url https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/AVX2/cu121 