import chromadb
from chromadb.config import Settings

class ChromaDB:
    def __init__(self, persist_directory="memory/chroma_db"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        self.short_term = self.client.get_or_create_collection("short_term_memory")
        self.long_term = self.client.get_or_create_collection("long_term_memory")

    def add(self, content, memory_type="short", tags=None):
        print(f"[📥] Embedding to Chroma: {content[:60]}")
        collection = self.short_term if memory_type == "short" else self.long_term
        metadata = {"tags": tags} if tags else {}
        
        # Use content hash as ID to avoid duplicates
        import hashlib
        content_id = hashlib.md5(content.encode()).hexdigest()
        
        collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[content_id]
        )

    def query_similar(self, query, memory_type="short", n_results=3):
        collection = self.short_term if memory_type == "short" else self.long_term
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results["documents"][0] if results["documents"] else [] 