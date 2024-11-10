# app/main.py
from fastapi import FastAPI
from app.services import SchemaService, ExtractionService  # Fix imports to use absolute imports
from app.models import SchemaDefinition, ExtractRequest

app = FastAPI(title="Dynamic Information Extractor")

@app.post("/schemas")
async def create_schema(request: SchemaDefinition):
    return {"schema_id": await SchemaService.create_schema(request)}

@app.get("/schemas")
async def list_schemas():
    return await SchemaService.list_schemas()

@app.get("/schemas/{schema_id}")
async def get_schema(schema_id: str):
    model_class, metadata = await SchemaService.load_schema_model(schema_id)
    return {
        "metadata": metadata,
        "schema": model_class.model_json_schema()
    }

@app.delete("/schemas/{schema_id}")
async def delete_schema(schema_id: str):
    return await SchemaService.delete_schema(schema_id)

@app.post("/extract")
async def extract_information(request: ExtractRequest):
    return await ExtractionService.extract_information(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)  # Updated to use module path