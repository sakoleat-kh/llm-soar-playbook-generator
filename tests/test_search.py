from app.services.chroma_service import search_techniques

results = search_techniques(
    "PowerShell executed an encoded command."
)

for r in results:
    print(r)