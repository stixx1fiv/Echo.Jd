FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip pip install pyyaml fastapi uvicorn pydantic

COPY . /app

RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/app"

RUN mkdir -p memory && \
    echo '{"short_term_memory": [], "long_term_memory": [], "scene_state": {}}' > memory/state.json && \
    mkdir -p memory/chroma_db

EXPOSE 8000

CMD ["python", "api_main.py"]