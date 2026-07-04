FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user compliance_app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download models at build time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
RUN python -c "from transformers import pipeline; pipeline('zero-shot-classification', model='typeform/distilbert-base-uncased-mnli', device=-1)"

COPY --chown=user compliance_app/ ./compliance_app/
COPY --chown=user main.py .

ENV PORT=7860
ENV CHROMA_PERSIST_DIR=/app/chroma_db
ENV USERS_FILE=/app/users.json
ENV ANONYMIZED_TELEMETRY=false

EXPOSE 7860

CMD ["python", "main.py"]
