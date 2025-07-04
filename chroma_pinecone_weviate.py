# -*- coding: utf-8 -*-
"""Vector Db's Compare

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QSag9pRgVvyRRh52-mtF0LF3lE_1Chod

# Load PDF and Split into Chunks
"""

# !pip uninstall -y protobuf
# !pip install protobuf==6.31.1 --force-reinstall --no-cache-dir

# import google.protobuf
# print(google.protobuf.__version__)

!pip install langchain_community pymupdf
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

pdf_path = "/content/APJAbdulKalam.pdf"  # 🔁 Replace this with your PDF path

loader = PyMuPDFLoader(pdf_path)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
split_docs = splitter.split_documents(docs)
documents = [doc.page_content for doc in split_docs]
metadatas = [{"source": doc.metadata.get("page", "unknown")} for doc in split_docs]

len(documents)
split_docs[0]

"""# Embedding Model - Jina AI"""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM

embedding_model_name = "jinaai/jina-embeddings-v2-base-code"
embedding_tokenizer = AutoTokenizer.from_pretrained(embedding_model_name, trust_remote_code=True)
embedding_model = AutoModel.from_pretrained(embedding_model_name, trust_remote_code=True)

def get_embedding(texts):
    inputs = embedding_tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = embedding_model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.cpu().numpy()

embeddings = get_embedding(documents)
embeddings

"""# Chroma Database"""

# # Step 2: Restart the runtime (IMPORTANT)
# import os
# os.kill(os.getpid(), 9)  # force restarts the Colab runtime

!pip install chromadb
from chromadb import Client
from chromadb.config import Settings

import google.protobuf
print(google.protobuf.__version__)

chroma_client = Client(Settings(anonymized_telemetry=False, persist_directory="./chroma_jina_db"))
collections = chroma_client.list_collections()

for collection in collections:
    print(f"Deleting collection: {collection.name}")
    chroma_client.delete_collection(name=collection.name)

chroma_collection = chroma_client.create_collection(name="Chroma_Collection")

chroma_collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=[f"doc{i}" for i in range(len(documents))],
    embeddings=embeddings.tolist()
)

"""# Pinecone Database"""

!pip install pinecone-client==4.0.0

from pinecone import Pinecone

pc = Pinecone(api_key="pcsk_3p3bSz_5MEkGJeGRtMMiq57Zt9cXtcVMaN3UvmyokxYvYurnV4SdP1dg4ZnSoQGcyRMBXL")
index_name = "test2"

index = pc.Index(index_name)

pinecone_data = [
    {
        "id": f"doc{i}",
        "values": embeddings[i].tolist(),
        "metadata": {
            "text": documents[i],
            "source": metadatas[i]["source"]
        }
    }
    for i in range(len(documents))
]

index.upsert(vectors=pinecone_data)

"""# Weviate Database"""

!pip install -U weaviate-client

WEAVIATE_URL="8nzs5auetcay3wetgzuxjw.c0.asia-southeast1.gcp.weaviate.cloud"
WEAVIATE_API_KEY="T2t0UCtJSlJPemdjcUgyYl9BSDVXNXZIeE9UVURFOHlLNUh6ZjlPWU5OdG9zQnBLVjBQSVJsbmdLMDFjPV92MjAw"

import weaviate
from weaviate.classes.init import Auth
import os
import uuid

# Best practice: store your credentials in environment variables
weaviate_url = WEAVIATE_URL
weaviate_api_key = WEAVIATE_API_KEY

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)

print(client.is_ready())  # Should print: `True`

COLLECTION_NAME="test1"
weviate_collection = client.collections.get(COLLECTION_NAME)

with weviate_collection.batch.fixed_size(batch_size=500) as batch:
    for doc, meta, embedding in zip(documents, metadatas, embeddings):
        batch.add_object(
            properties={
                "text": doc,
                "source": str(meta["source"])
            },
            vector=embedding.tolist(),
            uuid=str(uuid.uuid4())
        )
        if batch.number_errors > 10:
            print("❌ Too many errors in batch, stopping upload.")
            break

# Optional: Check failed uploads
if weviate_collection.batch.failed_objects:
    print("❗ Failed imports:", len(weviate_collection.batch.failed_objects))

"""# Pg Vector Database"""

!pip install pgvector
!pip install psycopg[binary]

import psycopg
from pgvector.psycopg import register_vector

# Connect to DB and register pgvector
conn = psycopg.connect(dbname='pgvector_example', autocommit=True)
conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
register_vector(conn)

# Drop and create table
conn.execute('DROP TABLE IF EXISTS rag_chunks')
conn.execute('CREATE TABLE rag_chunks (id bigserial PRIMARY KEY, content text, embedding vector(768), metadata text)')

# Store data
cur = conn.cursor()
with cur.copy('COPY rag_chunks (content, embedding, metadata) FROM STDIN WITH (FORMAT BINARY)') as copy:
    copy.set_types(['text', 'vector', 'text'])
    for content, embedding, meta in zip(documents, embeddings, metadatas):
        copy.write_row([content, embedding, str(meta)])



"""# Query"""

query = "Who is Abdul Kalam?"
query_embedding_vector = get_embedding([query])[0].tolist()

"""# Chroma Results"""

chroma_results = chroma_collection.query(
    query_embeddings=query_embedding_vector,
    n_results=3
)
chroma_relavant_docs = chroma_results["documents"][0]
chroma_scores = chroma_results["distances"][0]

print("\n🔍 Retrieved Chunks from Chroma:")
for doc, score in zip(chroma_relavant_docs, chroma_scores):
    print(f"- Score: {score:.4f}")
    print(f"  Text: {doc.strip()}")
    print()

"""# Pinecone Results"""

pinecone_results = index.query(vector=query_embedding_vector, top_k=3, include_metadata=True)

pinecone_relavant_docs = [(match['metadata']['text'], match['score']) for match in pinecone_results['matches']]

print("\n🔍 Retrieved Chunks from Pinecone:")
for doc, score in pinecone_relavant_docs:
    print(f"- Score: {score:.4f}")
    print(f"  Text: {doc}")
    print()

"""# Weviate Results"""

weviate_results = weviate_collection.query.near_vector(
    near_vector=query_embedding_vector,
    limit=3,
    return_metadata=["distance"]
)

weviate_relavant_docs = [
    (obj.properties["text"], obj.metadata.distance)
    for obj in weviate_results.objects
]

print("\n🔍 Retrieved Chunks from Weaviate:")
for doc, distance in weviate_relavant_docs:
    print(f"- Score: {distance:.4f}")
    print(f"  Text: {doc}")
    print()

"""| DB       | Min (Best) | Max (Worst) |
| -------- | ---------- | ----------- |
| Chroma   | 0.0        | 150–300+    |
| Pinecone | 0.7–1.0    | 0.0–0.6     |
| Weaviate | 0.0        | 2–10        |

# LLM
"""

from transformers import pipeline

llm_model_name = "google/flan-t5-base"
llm_tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
llm_model = AutoModelForSeq2SeqLM.from_pretrained(llm_model_name)

llm_pipe = pipeline(
    "text2text-generation",
    model=llm_model,
    tokenizer=llm_tokenizer,
    max_length=512,
    device=0 if torch.cuda.is_available() else -1
)

chroma_context = "\n\n".join([
    f"Chunk {i+1}:\n{text.strip()}"
    for i, text in enumerate(chroma_relavant_docs)
])

print(f"\n🧠 Question: {query}")

final_input = f"""You are a highly knowledgeable assistant.
Your job is to answer the following question **only** based on the provided context.

Summarize the identity, contributions, and role of the person mentioned in the question.

Context:
{chroma_context}

Question: {query}
Answer:"""

chroma_response = llm_pipe(final_input)[0]["generated_text"]
print("\n✅ Chroma Answer:\n", chroma_response)

pinecone_context = "\n\n".join([
    f"{text.strip()}"
    for text, score in pinecone_relavant_docs
])

print(f"\n🧠 Question: {query}")

final_input = f"""
You are an expert assistant.
Answer the following question strictly based on the provided context."

Context:
{pinecone_context}

Question: {query}
Answer:"""

pinecone_response = llm_pipe(final_input)[0]["generated_text"]
print("\n✅ Pinecone Answer:\n", pinecone_response)

weviate_context = "\n\n".join([
    f"{text.strip()}"
    for text, score in weviate_relavant_docs
])

print(f"\n🧠 Question: {query}")

final_input = f"""
You are an expert assistant.
Answer the following question strictly based on the provided context."

Context:
{weviate_context}

Question: {query}
Answer:"""

weviate_response = llm_pipe(final_input)[0]["generated_text"]
print("\n✅ Weviate Answer:\n", weviate_response)
