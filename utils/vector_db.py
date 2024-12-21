import faiss

def store_data_in_vector_db(model, data):
    """Encode and store the entire data in a vector database."""
    vectors = model.encode(data)
    faiss.normalize_L2(vectors)

    dimension = vectors.shape[1]
    # index = faiss.IndexFlatL2(dimension)
    index = faiss.IndexHNSWFlat(dimension, 32)  # HNSW with 32 neighbors
    index.add(vectors)

    return index

def query_vector_db(prompt, model, index, data, k=3):
    """Query the vector database and retrieve relevant data."""
    prompt_vector = model.encode([prompt])
    faiss.normalize_L2(prompt_vector)

    distances, indices = index.search(prompt_vector, k)
    top_results = [data[idx] for idx in indices[0]]

    return top_results