def retrieve(query, collection, top_k=5):
    q_emb = GeminiEmbeddings().embed_query(query)
    docs = collection.query(query_embeddings=[q_emb], n_results=top_k)
    ranked = rank_by_relevance(docs)
    return ranked
