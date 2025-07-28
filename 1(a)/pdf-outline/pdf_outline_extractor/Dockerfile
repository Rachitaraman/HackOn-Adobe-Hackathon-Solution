# FROM python:3.10-slim

# RUN apt-get update && apt-get install -y \
#     tesseract-ocr \
#     tesseract-ocr-eng \
#     tesseract-ocr-hin \
#     tesseract-ocr-deu \
#     tesseract-ocr-fra \
#     libtesseract-dev \
#     poppler-utils \
#     build-essential \
#     libglib2.0-0 \
#     libsm6 \
#     libxext6 \
#     libxrender-dev \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# COPY requirements.txt ./


# RUN pip install --no-cache-dir -r requirements.txt

# COPY app/ ./app
# COPY pdf_extract_kit/ ./pdf_extract_kit/
# ENV PYTHONPATH=/app


# CMD ["python", "app/main.py"]

# Use lightweight base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    gcc \
    libsm6 \
    libxext6 \
    libxrender-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set the default command
CMD ["python", "app/main.py"]
