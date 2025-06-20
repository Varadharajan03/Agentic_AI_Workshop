def retrieve_context(query, vectordb, k=3):
    return vectordb.similarity_search(query, k=k)
