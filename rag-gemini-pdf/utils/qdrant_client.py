#QdrantClient-Main class to interact with Qdrant (connect, search, insert, etc.)
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
#PointStruct-Used to represent a single data point in Qdrant
#uuid: For generating unique IDs
import uuid, os
from dotenv import load_dotenv
load_dotenv()

#uuid-generate unique identifiers for vector points

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

#function to create a Qdrant collection (if it doesn’t exist) or recreate it (if clear_existing=True).
def create_or_get_collection(collection_name="doc_chunks", clear_existing=False):
    try:
        # Check if collection exists and get its info
        collections = qdrant.get_collections().collections
        #.collections gives you the list of individual collection metadata objects.
        #get_collections() fetches all existing collections in your Qdrant instance.
        #Checks if a collection with the desired name already exists.
        existing_collection = next((c for c in collections if c.name == collection_name), None)
        
        if existing_collection:
            if clear_existing:
                print(f"Clearing existing collection '{collection_name}' for new document...")
                qdrant.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
                )
                return collection_name
                
            # Get collection info to check vector size
            #Get full configuration details of the existing collection.
            collection_info = qdrant.get_collection(collection_name)
            expected_size = 768  # Google embedding-001 model dimension. size=768: Vector dimension (matches Google Gemini embedding model)
            
            if hasattr(collection_info.config.params.vectors, 'size'):#Checks if the vectors object has a property called size.
                actual_size = collection_info.config.params.vectors.size
            else:
                # Handle named vectors case
                #list(...)[0] converts it to a list and picks the first vector (assuming only one type).
                #.size then gives the dimension of this first vector.
                actual_size = list(collection_info.config.params.vectors.values())[0].size
            
            if actual_size != expected_size:
                print(f"Collection exists but has wrong vector size ({actual_size} vs {expected_size}). Recreating...")
                qdrant.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=expected_size, distance=Distance.COSINE)
                )
        else:
            # Create new collection
            qdrant.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
    except Exception as e:
        print(f"Error managing collection: {e}")
        # Fallback: recreate collection
        qdrant.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
    
    return collection_name

def upload_chunks_to_qdrant(chunks, embed_fn, collection_name="doc_chunks", document_id=None):
    #embed_fn-A function that converts a list of text chunks into a list of vectors (embeddings).
    #document_id: Optional. If given, will tag all chunks with this ID. If not, a unique ID is generated.
    #chunks: A list of text chunks (strings) to be embedded and stored.
    try:
        vectors = embed_fn(chunks)
        #Converts each chunk (text) into a numeric vector representation 
        print(f"Generated {len(vectors)} vectors, each with {len(vectors[0])} dimensions")
        
        
        # Generate document ID if not provided
        if document_id is None:
            import time
            document_id = f"doc_{int(time.time())}"
            #time.time() returns the current time in seconds
        
        points = [
            PointStruct(
                id=uuid.uuid4().int >> 64, 
                vector=vec, #The embedding vector for that chunk.
                payload={ #Metadata stored along with the vector:
                    "text": chunk, #The original chunk.
                    "document_id": document_id, #Used to group all chunks from the same document.
                    "chunk_index": i #The index of the chunk (0-based).
                }
            )
            for i, (chunk, vec) in enumerate(zip(chunks, vectors))
        ]
        qdrant.upsert(collection_name=collection_name, points=points) #Uploads (or updates) all the points into the Qdrant collection.
        print(f"Uploaded {len(points)} chunks for document: {document_id}") #Displays how many chunks were uploaded.
        return document_id #Returns the document_id for reference/tracking.
        
    except Exception as e:
        print(f"Error uploading chunks: {e}")
        if "Vector dimension error" in str(e):
            print("Vector dimension mismatch detected. Recreating collection...")
            create_or_get_collection(collection_name)
            # Retry upload after recreating collection
            vectors = embed_fn(chunks)
            points = [
                PointStruct(
                    id=uuid.uuid4().int >> 64, 
                    vector=vec, 
                    payload={
                        "text": chunk,
                        "document_id": document_id,
                        "chunk_index": i
                    }
                )
                for i, (chunk, vec) in enumerate(zip(chunks, vectors))
            ]
            qdrant.upsert(collection_name=collection_name, points=points)
            return document_id
            #[Chunks] --(embed_fn)--> [Vectors] --(with metadata)--> [PointStructs] --> Qdrant Upload
            
            
#This function searches for the top_k most semantically similar text chunks 
# in the Qdrant vector database based on a user’s query.
def search_similar_chunks(query, embed_fn, collection_name="doc_chunks", top_k=5, document_id=None):
    query_vector = embed_fn([query])[0] #Used to produce query vector
    
    # Add filter for specific document if provided
    search_filter = None #We initialize search_filter as None. This means no filtering by default.
    if document_id:
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    
    results = qdrant.search(
        collection_name=collection_name, 
        query_vector=query_vector, 
        limit=top_k,
        query_filter=search_filter
    )
    return [hit.payload["text"] for hit in results]
