from fastapi import FastAPI, Request

app = FastAPI(
    title="Shuffle API Test Server",
    description="Local simulator for testing Shuffle workflow imports.",
    version="1.0.0"
)

@app.post("/api/v1/workflows")
async def import_workflow(request: Request):
    workflow = await request.json()

    print("-" * 50)
    print("Workflow received by Shuffle API Test Server!")
    print("-" * 50)
    print(workflow)

    return {
        "status": "success",
        "workflow_id": "test-12345",
        "message": "Workflow imported successfully."
    }