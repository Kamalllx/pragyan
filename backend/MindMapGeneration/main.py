from fastapi import FastAPI, File, UploadFile, Form
from mindmap_generator import MindmapGenerator
import pdfplumber
import os
import json
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sentence_transformers import SentenceTransformer
import hashlib
import os
from mindmap_generator import MindmapGenerator

from dotenv import load_dotenv
load_dotenv()
import os
import time


PDF_CACHE_DIR = "./pdf_cache"
MINDMAPS_DIR = "./mindmaps"
os.makedirs(PDF_CACHE_DIR, exist_ok=True)
os.makedirs(MINDMAPS_DIR, exist_ok=True)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")  # Set this in your shell or .env

app = FastAPI()
generator = MindmapGenerator(api_key=GROQ_API_KEY)

def get_pdf_hash(pdf_path):
    with open(pdf_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]

def chunk_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        chunks = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                for para in text.split('\n\n'):
                    if para.strip():
                        chunks.append({"text": para.strip(), "page": i+1})
    return chunks

def preprocess_and_embed(pdf_path):
    pdf_hash = get_pdf_hash(pdf_path)
    embeddings_path = f"./embeddings_{pdf_hash}.npy"
    chunks_path = f"./chunks_{pdf_hash}.json"
    # If already processed, load
    if os.path.exists(embeddings_path) and os.path.exists(chunks_path):
        embeddings = np.load(embeddings_path)
        with open(chunks_path, "r") as f:
            chunks = json.load(f)
        return embeddings, chunks
    # Otherwise, process
    chunks = chunk_pdf(pdf_path)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedding_model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")
    np.save(embeddings_path, embeddings)
    with open(chunks_path, "w") as f:
        json.dump(chunks, f)
    return embeddings, chunks

def get_relevant_chunks(query, embeddings, chunks, top_k=15):
    top_k = min(top_k, len(chunks))
    query_emb = embedding_model.encode([query]).astype("float32")
    nn = NearestNeighbors(n_neighbors=top_k, metric="euclidean")
    nn.fit(embeddings)
    distances, indices = nn.kneighbors(query_emb)
    return [chunks[i]["text"] for i in indices[0]]

def filter_irrelevant_chunks(chunks):
    # Define keywords/phrases to skip (less aggressive, more precise)
    skip_keywords = [
        'activity', 'exercise', 'did you know', 'what you have learnt',
        'extended learning', 'project', 'summary', 'true or false', 'classify', 'harmful changes'
    ]
    filtered = []
    for chunk in chunks:
        text = chunk["text"].strip().lower()
        # Only skip if the text starts with or is exactly a skip keyword/phrase
        if any(text.startswith(kw) or text == kw for kw in skip_keywords):
            continue
        filtered.append(chunk)
    print(f"[DEBUG] Chunks before filtering: {len(chunks)}, after filtering: {len(filtered)}")
    return filtered


@app.post("/generate-mindmap/")
async def generate_mindmap(file: UploadFile = File(...), query: str = Form(...)):
    try:
        print("[DEBUG] Received request for mindmap generation.")
        pdf_path = os.path.join(PDF_CACHE_DIR, file.filename)
        contents = await file.read()
        with open(pdf_path, "wb") as f:
            f.write(contents)
        print(f"[DEBUG] Saved PDF to {pdf_path}")
        embeddings, chunks = preprocess_and_embed(pdf_path)
        print(f"[DEBUG] Loaded {len(chunks)} chunks and embeddings shape {embeddings.shape}")

        # Summarize each chunk (with throttling)
        # Instead of summarizing each chunk and joining, do:
        texts = [chunk["text"] for chunk in chunks]
        combined_summary = generator.hierarchical_summarize(texts)
        print(f"[DEBUG] Final combined summary length: {len(combined_summary)}")
        mindmap_json = generator.generate_mindmap(combined_summary)
        from mindmap_generator import summaries

        combined_summary = "\n".join(summaries)
        print(f"[DEBUG] Combined summary length: {len(combined_summary)}")

        mindmap_json = generator.generate_mindmap(combined_summary)
        print(f"[DEBUG] LLM returned mindmap: {mindmap_json[:500]}..." if isinstance(mindmap_json, str) else "[DEBUG] LLM returned mindmap object.")

        # Save mindmap JSON to file for reuse
        hash_input = (file.filename + query).encode("utf-8")
        unique_hash = hashlib.sha256(hash_input).hexdigest()[:16]
        mindmap_path = os.path.join(MINDMAPS_DIR, f"{file.filename}_{unique_hash}.json")
        with open(mindmap_path, "w") as f:
            f.write(mindmap_json)
        print(f"[DEBUG] Saved mindmap JSON to {mindmap_path}")

        return {"mindmap": mindmap_json, "mindmap_file": mindmap_path}
    except Exception as e:
        print(f"[ERROR] Exception in /generate-mindmap/: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}