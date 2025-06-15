import chromadb
from services.embedder import embed_chunks, embed_query
import uuid
from app.utils.mongo import data


def store_chunks(raw_chunks):
   
    texts = [chunk.strip() for chunk in raw_chunks if isinstance(chunk, str) and chunk.strip()]
    if not texts:
        print("⚠️ No valid chunks to store.")
        return

    embeddings = embed_chunks(texts)
    if isinstance(embeddings[0], float):
        embeddings = [embeddings] 
    print("Done 4")

    documents = []
    for text, embedding in zip(texts, embeddings):
        doc = {
            "_id": str(uuid.uuid4()),
            "chunk": text,
            "embedding": embedding,
        }
        documents.append(doc)
    try:
        data.insert_many(documents)
        print(f"Stored {len(documents)} chunks in MongoDB.")
    except Exception as e:
        print("Failed to store chunks:", e)



def search_chunks(query, top_k, threshold):
    query_embedding = embed_query(query)
    try:
        pipeline = [
            {
                "$search": { 
                    "knnBeta": {
                    "vector": query_embedding,
                    "path": "embedding",
                    "k": top_k
                }
                }
            },
            {
                "$project": {
                    "chunk": 1,
                    "score": { "$meta": "searchScore" }
                }
            }
        ]

        results = list(data.aggregate(pipeline))
        # print("Result: ", results)
        # print("Res of Search: ", [
        #     {"text": r["chunk"], "score": r["score"]}
        #     for r in results if r["score"] >= threshold
        # ])

        # Filter by threshold (lower = more similar)
        return [
            {"text": r["chunk"], "score": r["score"]}
            for r in results if r["score"] >= threshold
        ]
        

    except Exception as e:
        print("MongoDB Vector Search failed:", e)
        return []

 




    
