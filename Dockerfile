# Render.com Dockerfile — cloud-only (Gemini embeddings v3 + LLM)
# Cache bust: 2026-05-22-v3
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn==0.30.6 \
    chromadb==0.5.5 \
    openpyxl==3.1.5 \
    python-docx==1.1.2 \
    google-genai==1.9.0 \
    python-dotenv==1.0.1 \
    reportlab==4.2.5 \
    arabic-reshaper==3.0.0 \
    python-bidi==0.6.3 \
    httpx==0.28.1

ARG CACHE_BUST=3
COPY chroma_db/ /app/chroma_db_seed/
COPY backend/ .
COPY data-files/ /app/data-files/

ENV EMBEDDING_SOURCE=gemini

EXPOSE 8000

CMD ["python", "render_start.py"]
