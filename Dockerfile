FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud CLI
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

RUN apt-get update && apt-get install -y google-cloud-cli && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🔍 Checking gcloud authentication..."\n\
if [ ! -f ~/.config/gcloud/application_default_credentials.json ]; then\n\
    echo "❌ No gcloud authentication found"\n\
    echo "Please run: gcloud auth login"\n\
    echo "Then: gcloud config set project YOUR_PROJECT_ID"\n\
    echo ""\n\
    echo "Starting interactive shell..."\n\
    /bin/bash\n\
else\n\
    echo "✅ gcloud authentication found"\n\
    echo "Starting FabricStudio Controller..."\n\
    gunicorn -w 4 -b 0.0.0.0:8000 app:app\n\
fi' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

CMD ["/app/start.sh"]
