from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.models.database import SessionLocal
from app.models.technique import Technique

CHROMA_PATH = "data/chroma"

embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

client = PersistentClient(path=CHROMA_PATH)
collection =client.get_or_create_collection(
    name="attack_techniques",
    embedding_function=embedding_function,
)

def build_attack_index():
    db = SessionLocal()

    try:
        technique = db.query(Technique).all()

        if not technique:
            print("No techniques found in database.")
            return

        try:
            client.delete_collection("attack_techniques")
        except Exception:
            pass

        collection = client.get_or_create_collection(
            name="attack_techniques",
            embedding_function=embedding_function,
        )

        ids = []
        documents = []
        metadatas = []

        for tech in technique:
            ids.append(tech.technique_id)

            documents.append(
                f"{tech.name}: {tech.description}"
            )

            metadatas.append(
                {
                    "technique_id": tech.technique_id,
                    "name": tech.name,
                    "tactics": ",".join(tech.tactics or {}),
                    "data_sources": ",".join(tech.data_sources or {}),
                }
            )

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        print(f"Index {len(ids)} ATT&CK techniques.")

    finally:
        db.close()

def search_techniques(query: str, n_results: int =5 ) -> list:
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )
    output = []

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for technique_id, document, metadata, distance in zip(
        ids,
        docs,
        metas,
        distances,
    ):
        output.append(
            {
                "technique_id": technique_id,
                "name": metadata.get("name"),
                "document": document,
                "tactics": metadata.get("tactics"),
                "distance": distance,
            }
        )
    return output

if __name__ == "__main__":
    build_attack_index()



