# We will build a Python RAG app that does this:
- Read a PDF
- Split it into chunks
- Convert chunks into embeddings
- Store embeddings in FAISS
- Retrieve the best chunks for a question
- Send retrieved text + question to an LLM
- Return the final answer

---

## 2) Install packages
```bash
pip install pypdf sentence-transformers faiss-cpu numpy transformers torch
```

---

## 3) Folder structure
```text
rag_project/
│
├── data/
│   └── employee_leave_policy.pdf
│
└── app.py
```

---

## 4) Full Python code
```python
import os
import numpy as np
import faiss
import torch
torch.set_num_threads(1)
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


PDF_PATH = "data/Employee-Handbook.pdf"


def load_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def build_faiss_index(chunks, embed_model):
    embeddings = embed_model.encode(chunks, convert_to_numpy=True)

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    return index, embeddings


def retrieve_chunks(query, chunks, index, embed_model, top_k=3):
    query_embedding = embed_model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)

    results = []
    for i in indices[0]:
        if i != -1:
            results.append(chunks[i])

    return results


def answer_question(question, retrieved_chunks, generator):
    tokenizer, model = generator
    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
You are a helpful assistant.
Answer the question using only the context below.
If the answer is not in the context, say you do not know.

Context:
{context}

Question:
{question}

Answer:
"""

    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=150, do_sample=False)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def main():
    if not os.path.exists(PDF_PATH):
        print(f"PDF not found at: {PDF_PATH}")
        return

    print("Loading PDF...")
    text = load_pdf_text(PDF_PATH)

    print("Chunking text...")
    chunks = chunk_text(text, chunk_size=250, overlap=50)

    print(f"Created {len(chunks)} chunks.")

    print("Loading embedding model...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Building FAISS index...")
    index, _ = build_faiss_index(chunks, embed_model)

    print("Loading generation model...")
    # You can replace this model with any local or hosted LLM later
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
    generator = (tokenizer, model)

    try:
        while True:
            question = input("\nAsk a question (type 'exit' to stop): ").strip()
            if question.lower() == "exit":
                break

            relevant_chunks = retrieve_chunks(question, chunks, index, embed_model, top_k=3)
            answer = answer_question(question, relevant_chunks, generator)

            print("\nAnswer:")
            print(answer)
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")


if __name__ == "__main__":
    main()
```

---

## 5) How it works

### Embedding model
`SentenceTransformer("all-MiniLM-L6-v2")` converts each chunk into a vector.

### FAISS
FAISS stores vectors and finds the most similar chunks quickly.

### Generation model
`flan-t5-base` reads the retrieved context and creates the final answer.

---

## 6) Example of a good test document

Create a PDF with sections like:
1. Leave Policy
2. Casual Leave Rules
3. Sick Leave Rules
4. Holiday Policy
5. Attendance Rules
6. Leave Approval Process

That will make it very easy to test retrieval.

---

## 7) Example questions to test
- What is the leave approval process?
- How many sick leaves are allowed?
- Can leave be carried forward?
- What happens if I am absent without notice?

---

## 8) When this setup is enough

This is good for:
- learning RAG
- small PDFs
- proof of concept
- internal demos

For bigger systems later, you can add:
- better chunking
- metadata
- reranking
- chat memory
- Streamlit UI
- FastAPI backend
- multiple PDFs

I can turn this into a Streamlit chatbot app next, using the same PDF example.

---

## Get me an example PDF from internet to download

Here are some excellent PDFs you can directly download and use for your first RAG project:

### Recommended PDF (Best for Beginners)
**Employee Handbook PDF**

This is the best one to start with because:
- structured sections
- policies and FAQs
- easy retrieval testing
- realistic enterprise use case

#### Download Link
- **Employee Handbook PDF**

*Source overview:* contains employment basics, policies, conduct rules, leave information, and company procedures.

### Alternative PDFs

#### HR Policy PDF
*Good for:*
- policy retrieval
- leave rules
- compliance chatbot

- **HR Policy PDF**

#### Sample Employee Handbook Template
*Good for:*
- multi-section retrieval
- chunking experiments
- metadata filtering

- **Sample Employee Handbook Template PDF**

### Questions You Can Test in Your RAG

After downloading the PDF, try queries like:
- What is the leave approval process?
- What happens during probation?
- How are holidays handled?
- What is the attendance policy?
- Can employees work remotely?