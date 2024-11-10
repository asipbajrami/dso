# app/services.py
import uuid
import json
import importlib.util
import sys
from datetime import datetime, UTC
from typing import Type, Tuple
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from trustcall import create_extractor
from pydantic import BaseModel

from app.models import SchemaDefinition, SchemaInfo, ExtractRequest, SchemaField
from app.utils import SCHEMAS_DIR, generate_pydantic_model_code

class SchemaService:
    @staticmethod
    async def create_schema(request: SchemaDefinition) -> str:
        try:
            schema_id = str(uuid.uuid4())
            model_name = f"{request.name}_{schema_id.replace('-', '_')}"

            # Generate model code
            model_code = generate_pydantic_model_code(request.fields, model_name)

            # Save schema files
            schema_path = SCHEMAS_DIR / f"{schema_id}.py"
            metadata_path = SCHEMAS_DIR / f"{schema_id}.meta.json"

            with open(schema_path, 'w') as f:
                f.write(model_code)

            metadata = {
                "id": schema_id,
                "name": request.name,
                "description": request.description,
                "created_at": str(datetime.now(UTC))
            }

            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)

            return schema_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def load_schema_model(schema_id: str) -> Tuple[Type[BaseModel], SchemaInfo]:
        schema_path = SCHEMAS_DIR / f"{schema_id}.py"
        metadata_path = SCHEMAS_DIR / f"{schema_id}.meta.json"

        if not schema_path.exists() or not metadata_path.exists():
            raise HTTPException(status_code=404, detail=f"Schema not found: {schema_id}")

        try:
            # Load metadata
            with open(metadata_path, 'r') as f:
                metadata = SchemaInfo(**json.load(f))

            # Load dynamic model
            spec = importlib.util.spec_from_file_location(f"schema_{schema_id}", schema_path)
            if not spec or not spec.loader:
                raise ImportError(f"Failed to load schema module: {schema_id}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            model_name = f"{metadata.name}_{schema_id.replace('-', '_')}"
            return getattr(module, model_name), metadata
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading schema: {str(e)}")

class ExtractionService:
    @staticmethod
    async def extract_information(request: ExtractRequest):
        try:
            # Handle both schema_id and direct fields cases
            if request.schema_id:
                dynamic_model, _ = await SchemaService.load_schema_model(request.schema_id)
                model_name = dynamic_model.__name__
            elif request.fields:
                # Generate temporary model from direct fields
                temp_model_name = f"TempModel_{str(uuid.uuid4()).replace('-', '_')}"
                model_code = generate_pydantic_model_code(request.fields, temp_model_name)

                # Create module for temporary model
                module = type(sys)(temp_model_name)
                exec(model_code, module.__dict__)
                sys.modules[temp_model_name] = module

                dynamic_model = getattr(module, temp_model_name)
                model_name = temp_model_name
            else:
                raise HTTPException(status_code=400, detail="Either schema_id or fields must be provided")

            llm = ChatOpenAI(model="gpt-4o-mini", api_key=request.api_key)
            extractor = create_extractor(
                llm,
                tools=[dynamic_model],
                tool_choice=model_name,
                enable_inserts=True
            )

            result = extractor.invoke({
                "messages": [{
                    "role": "user",
                    "content": f"Extract information from this text according to the schema. Do not hallucinate anything:\n\n{request.text}"
                }]
            })

            return {"extracted_data": [
                response.model_dump(exclude_none=True)
                for response in result["responses"]
            ]}

        except HTTPException as he:
            raise he
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            elif "invalid_api_key" in str(e).lower():
                raise HTTPException(status_code=401, detail="Invalid API key")
            else:
                raise HTTPException(status_code=500, detail=str(e))