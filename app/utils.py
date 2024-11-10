from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import SchemaField  # Import SchemaField from models.py

# Constants
SCHEMAS_DIR = Path("schema_models")
SCHEMAS_DIR.mkdir(exist_ok=True)

TYPE_MAPPING = {
    "string": "str",
    "int": "int",
    "boolean": "bool",
    "float": "float",
    "object": "object",
    "array": "array"
}

IMPORTS_TEMPLATE = '''from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
'''

@dataclass
class ModelGenerator:
    """Class to handle Pydantic model generation logic."""
    schema_fields: List[SchemaField]
    model_name: str

    def generate(self) -> str:
        """Generate complete Pydantic model code."""
        nested_models = self._generate_nested_models(self.schema_fields, self.model_name)
        main_model = self._generate_main_model()

        # Combine all code parts
        code_parts = [IMPORTS_TEMPLATE]
        code_parts.extend(model.code for model in nested_models)
        code_parts.append(main_model)

        return "\n\n".join(code_parts)

    def _generate_nested_models(self, fields: List[SchemaField], parent_name: str) -> List[ModelComponent]:
        """Generate nested models recursively."""
        models = []

        for field in fields:
            # Handle enum fields
            if field.enum_values:
                models.append(self._generate_enum_model(field, parent_name))

            # Handle nested objects and arrays
            if field.type in ["object", "array"] and field.children:
                nested_name = self._get_nested_model_name(field, parent_name)
                models.extend(self._generate_nested_models(field.children, nested_name))
                models.append(self._generate_nested_class(field, nested_name))

        return models

    def _generate_main_model(self) -> str:
        """Generate the main model class."""
        fields_code = []
        for field in self.schema_fields:
            field_type = self._get_field_type(field, self.model_name)
            field_def = self._generate_field_definition(field, field_type)
            fields_code.append(f"    {field_def}")

        return f"class {self.model_name}(BaseModel):\n" + "\n".join(fields_code)

    def _get_field_type(self, field: SchemaField, parent_name: str) -> str:
        """Determine the field type with proper handling for special cases."""
        if field.enum_values:
            return f"{parent_name}_{field.key}_enum"
        elif field.type == "object":
            return f"{parent_name}_{field.key}"
        elif field.type == "array":
            return f"List[{parent_name}_{field.key}_item]"
        else:
            return TYPE_MAPPING.get(field.type, "str")

    @staticmethod
    def _generate_field_definition(field: SchemaField, field_type: str) -> str:
        """Generate a field definition with proper escaping and formatting."""
        if not field.required:
            field_type = f"Optional[{field_type}]"

        escaped_description = escape_description(field.description)
        default_part = ", default=None" if not field.required else ""

        return (f'{field.key}: {field_type} = Field('
                f'description="{escaped_description}"{default_part})')

    @staticmethod
    def _get_nested_model_name(field: SchemaField, parent_name: str) -> str:
        """Generate appropriate name for nested models."""
        base_name = f"{parent_name}_{field.key}"
        return f"{base_name}_item" if field.type == "array" else base_name

    def _generate_enum_model(self, field: SchemaField, parent_name: str) -> ModelComponent:
        """Generate enum class code."""
        enum_name = f"{parent_name}_{field.key}_enum"
        enum_values = [
            f"    {clean_enum_key(value)} = '{value.replace('\'', '\\\'')}'"
            for value in field.enum_values or []
        ]
        enum_code = f"class {enum_name}(str, Enum):\n" + "\n".join(enum_values)
        return ModelComponent(name=enum_name, code=enum_code)

    def _generate_nested_class(self, field: SchemaField, nested_name: str) -> ModelComponent:
        """Generate nested class code."""
        fields_code = []
        for child in field.children or []:
            field_type = self._get_field_type(child, nested_name)
            field_def = self._generate_field_definition(child, field_type)
            fields_code.append(f"    {field_def}")

        class_code = f"class {nested_name}(BaseModel):\n" + "\n".join(fields_code)
        return ModelComponent(name=nested_name, code=class_code)

@dataclass
class ModelComponent:
    """Class to represent a model component (class or enum)."""
    name: str
    code: str

def clean_enum_key(value: str) -> str:
    """Clean and format enum key, ensuring Python validity."""
    # Ensure string input
    if not isinstance(value, str):
        value = str(value)

    # Convert to uppercase and prefix
    key = "ENUM_" + value.upper()

    # Replace invalid characters with underscore
    key = re.sub(r'[^A-Z0-9]', '_', key)

    # Clean up multiple underscores and trailing underscores
    key = re.sub(r'_+', '_', key).rstrip('_')

    # Ensure valid Python identifier
    if not key.isidentifier():
        key = "ENUM_" + key

    return key

def escape_description(description: str) -> str:
    """Escape special characters in descriptions."""
    if not description:
        return ""

    return (description
            .replace('\\', '\\\\')  # Must be first
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '\\r')
            .replace('\t', '\\t'))

def generate_pydantic_model_code(schema_fields: List[SchemaField], model_name: str) -> str:
    """Generate Pydantic model code from schema fields."""
    generator = ModelGenerator(schema_fields, model_name)
    return generator.generate()