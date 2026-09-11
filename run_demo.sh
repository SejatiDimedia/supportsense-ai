#!/bin/bash
# SupportSense AI Quick Demo Launcher

set -e

echo "========================================================"
echo "          ⚡ Starting SupportSense AI Demo               "
echo "========================================================"

# Check virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment .venv not found. Please run setup first."
    exit 1
fi

echo "[1/2] Checking database and document collection..."
python3 -c "from app.persistence.db import init_db; init_db()"
python3 -c "from app.rag.embedder import VectorStoreManager; from pathlib import Path; VectorStoreManager().ingest_documents(Path('data/docs'))"

echo "[2/2] Launching Streamlit UI..."
streamlit run ui/streamlit_app.py
