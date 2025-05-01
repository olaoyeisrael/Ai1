import chromadb
from services.embedder import model as embed_model, embed_chunks, embed_query
import uuid

chroma_client = chromadb.Client()
chroma_client = chromadb.PersistentClient(path="./chromadb")
collection = chroma_client.get_or_create_collection(name="ai_tutor")

def store_chunks(raw_chunks):
    texts = [chunk.strip() for chunk in raw_chunks if isinstance(chunk, str) and chunk.strip()]
    if not texts:
        print("⚠️ No valid chunks to store.")
        return

    embeddings = embed_chunks(texts)
    if isinstance(embeddings[0], float):
        embeddings = [embeddings] 

    ids = [str(uuid.uuid4()) for _ in texts]
    try:
        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids
        )
        print(f"✅ Stored {len(texts)} chunks in ChromaDB.")
    except Exception as e:
        print("❌ Failed to store chunks:", e)


# def search_chunks(query, top_k=3):
#     # Step 1: Embed the query
#     query_embedding = embed_query(query)

#     # Step 2: Query ChromaDB
#     try:
#         results = collection.query(
#             query_embeddings=[query_embedding],
#             n_results=top_k,
#             include=["documents"]
#         )

#         # Step 3: Return results in clean format
#         return [
#             {"text": doc}
#             for doc in results["documents"][0]
#         ]

#     except Exception as e:
#         print("❌ Error during search:", e)
#         return []

def search_chunks(query, top_k, threshold):
    query_embedding = embed_query(query)

    try:
        results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "distances"]
        )

         # Get document texts and their distances
        documents = results["documents"][0]
        distances = results["distances"][0]
        # print(distances)
        # print(documents)
        # print(doc for doc, dist in zip(documents, distances) if dis)

        # Return only those under the threshold, formatted
        return [
            {"text": doc}
            for doc, dist in zip(documents, distances)
            if dist > threshold
        ]
    
    except Exception as e:
        print("❌ Error during search:", e)
        return []



    

def print_all_chunks():
    try:
        results = collection.get(include=["documents", "embeddings"])
        print("📦 All ChromaDB Chunks:\n")

        for i in range(len(results["documents"])):
            print(f"🔹 ID: {results['ids'][i]}")
            print(f"📝 Text: {results['documents'][i][:100]}...")
            print(f"📐 Embedding (first 5 dims): {results['embeddings'][i][:8]}")
            print("-" * 60)

        print(f"✅ Total chunks: {len(results['documents'])}")
    except Exception as e:
        print("❌ Error reading from ChromaDB:", e)