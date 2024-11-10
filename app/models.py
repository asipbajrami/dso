from datetime import datetime, UTC
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

class SchemaField(BaseModel):
    key: str = Field(..., description="Field identifier")
    type: str = Field(..., description="Data type of the field")
    description: str = Field(..., description="Description of the field")
    required: bool = Field(default=False, description="Whether the field is required")
    enum_values: Optional[List[str]] = Field(default=None, description="Possible values for enum types")
    children: Optional[List['SchemaField']] = Field(default=None, description="Nested fields for object and array types")

    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True,
        str_max_length=100,
    )

class SchemaDefinition(BaseModel):
    name: str = Field(
        ...,
        description="Name of the schema",
        pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$'
    )
    description: str = Field(..., description="Description of what this schema is for")
    fields: List[SchemaField] = Field(..., description="List of fields defining the schema")

class SchemaInfo(BaseModel):
    id: str = Field(..., description="Unique identifier for the schema")
    name: str = Field(..., description="Name of the schema")
    description: str = Field(..., description="Description of the schema")
    created_at: str = Field(..., description="Creation timestamp")

class ExtractRequest(BaseModel):
    text: str = Field(..., description="Text to extract information from", max_length=10000)
    schema_id: Optional[str] = Field(None, description="ID of previously created schema")
    fields: Optional[List[SchemaField]] = Field(None, description="Direct schema definition")
    api_key: str = Field(..., description="API key", min_length=32)

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not (v.startswith('sk-') and len(v) >= 32):
            raise ValueError("Invalid API key format")
        return v