import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

embedding_model = genai.embed_content
#This function allows you to generate embeddings (dense vector representations) 
# of texts for tasks like semantic search.
chat_model = genai.GenerativeModel("gemini-2.5-flash")
#chat_model is now an object that can handle natural language prompts via .generate_content().


def embed_fn(texts):
    #This uses Gemini 2.5’s embedding API, which returns embedding vectors for documents or queries. 
    # It is a different family of models from sentence-transformers.
    return [embedding_model(model="models/embedding-001", content=t, task_type="retrieval_document")["embedding"] for t in texts]
    #embedding_model(...) is called to generate an embedding vector.
    #model="models/embedding-001" specifies the embedding model to use (a Gemini model for embedding).
    #content=t is the text content being embedded.
    #task_type="retrieval_document" informs the model that the embeddings are meant for document retrieval tasks.
    
    
def generate_answer(context_chunks, query):
    context = "\n\n".join(context_chunks)
    prompt = f"""You are a helpful assistant that answers questions STRICTLY based on the provided document context.

IMPORTANT RULES:
1. Answer ONLY based on the information provided in the Context below
2. Do NOT use any external knowledge or previous conversation history
3. If the question cannot be answered from the provided context, respond with: "Sorry, this question is not related to the uploaded document or the information is not available in the document."
4. Be specific and quote relevant parts from the context when possible
5. Do not make assumptions or add information not present in the context

Context from the uploaded document:
\"\"\"
{context}
\"\"\"

Question: {query}

Answer based solely on the above context:"""

    response = chat_model.generate_content(prompt)
    return response.text.strip()
