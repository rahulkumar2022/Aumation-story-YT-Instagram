FROM node:22-bullseye

# Install Python 3, FFmpeg, and Chrome dependencies for Remotion
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    libasound2 \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip3 install edge-tts numpy scipy requests
RUN cd sample-video && npm install

# Make scripts executable
RUN chmod +x scripts/*.sh scripts/*.py

# Install cron jobs inside container
RUN ./scripts/setup_cron.sh

# Start cron daemon
CMD ["cron", "-f"]
