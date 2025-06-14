
# 🔍 Vector DB Integration Playground

This repository showcases how to integrate **six popular vector databases** using Python in a unified environment, with working examples built in **Google Colab**. Each vector DB supports storing, searching, and retrieving embeddings—ideal for building **RAG (Retrieval-Augmented Generation)** systems.

> 💡 **Live Notebook**: [Open in Google Colab](https://colab.research.google.com/drive/1QSag9pRgVvyRRh52-mtF0LF3lE_1Chod?usp=sharing)

---

## 📚 Vector Databases Covered

| Database     | Storage Type   | Hosting       | License        | Notes                              |
|--------------|----------------|---------------|----------------|------------------------------------|
| **Chroma**   | Local (disk)   | Local only    | Apache 2.0     | Lightweight, easy to start         |
| **Pinecone** | Cloud-hosted   | SaaS          | Proprietary    | Fast, managed, scale-ready         |
| **Weaviate** | Local / Cloud  | Self / SaaS   | BSD-3-Clause   | Schema, modules, hybrid search     |
| **Qdrant**   | Local / Cloud  | Self / SaaS   | Apache 2.0     | Strong filter support              |
| **Milvus**   | Local (Docker) | Self-hosted   | Apache 2.0     | High-performance, production-grade |
| **PGVector** | PostgreSQL ext | Self-hosted   | PostgreSQL     | Great for SQL-native applications  |

---

## 📁 Structure

Each section in the notebook covers:

- 🔧 Installation & Setup
- 🧠 Embedding Generation (using sentence-transformers / OpenAI / other)
- 📥 Insert Data (documents + embeddings)
- 🔍 Vector Search (`search_documents()` API per DB)
- 🧪 Output: Score + matching text

---

## 🛠️ Requirements

- Python 3.8+
- Google Colab (recommended)
- API Keys (for Pinecone, Weaviate cloud, etc.)
- Docker (for local Milvus,Qdrant if running manually)
- PostgreSQL + PGVector extension (for PGVector)

---

## 🚀 Run It Yourself

1. Clone this repo:
   ```bash
   git clone https://github.com/yourusername/VectorDatabase.git
   ```
2. Open the [Colab Notebook](https://colab.research.google.com/drive/1QSag9pRgVvyRRh52-mtF0LF3lE_1Chod?usp=sharing)
3. Set your API keys and configs in the appropriate cells.
4. Run all cells and compare the behavior of each vector DB.

---

## 📊 Use Case: RAG System Starter

This repo is a solid base for building a **Retrieval-Augmented Generation** system:
- Store chunked documents
- Embed using transformers
- Search relevant content
- Feed into LLM

---
