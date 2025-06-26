FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pyyaml

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "api_gateway/routes/api_hooks.py"]

