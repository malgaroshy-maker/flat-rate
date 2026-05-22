# Render.com Dockerfile — cloud LLM + local embeddings
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
    httpx==0.28.1 \
    sentence-transformers==3.1.1

# Pre-download MiniLM model during build (avoids 256MB download at runtime)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

COPY chroma_db/ /app/chroma_db_seed/
COPY backend/ .
COPY data-files/ /app/data-files/

ENV EMBEDDING_SOURCE=local

EXPOSE 8000

CMD ["python", "render_start.py"]
