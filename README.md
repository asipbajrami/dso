# Dynamic Structure Output 🎯

An advanced FastAPI service that allows you to create dynamic schemas and extract structured information from any text using AI. Perfect for automating data extraction from unstructured text like articles, job postings, product descriptions, or any other text format.

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/schema-extractor.git
cd schema-extractor
```

2. Create a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
# Basic run
uvicorn app.main:app --reload

# With custom host and port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📝 API Endpoints in Detail

### 1. Create Schema (`POST /schemas`)

Creates a new schema definition for information extraction. Here's a comprehensive example that shows all possible field types and configurations:

```json
POST /schemas
{
    "name": "ComprehensiveProduct",
    "description": "Schema for extracting detailed product information from descriptions",
    "fields": [
        {
            "key": "basic_info",
            "type": "object",
            "description": "Basic product information",
            "required": true,
            "children": [
                {
                    "key": "name",
                    "type": "string",
                    "description": "Product name",
                    "required": true
                },
                {
                    "key": "sku",
                    "type": "string",
                    "description": "Stock keeping unit",
                    "required": false
                },
                {
                    "key": "category",
                    "type": "string",
                    "description": "Product category",
                    "required": true,
                    "enum_values": ["Electronics", "Clothing", "Food", "Books"]
                }
            ]
        },
        {
            "key": "pricing",
            "type": "object",
            "description": "Pricing information",
            "required": true,
            "children": [
                {
                    "key": "amount",
                    "type": "float",
                    "description": "Price amount",
                    "required": true
                },
                {
                    "key": "currency",
                    "type": "string",
                    "description": "Currency code",
                    "required": true,
                    "enum_values": ["USD", "EUR", "GBP"]
                },
                {
                    "key": "discounted",
                    "type": "boolean",
                    "description": "Whether the product is discounted",
                    "required": false
                }
            ]
        },
        {
            "key": "specifications",
            "type": "array",
            "description": "Technical specifications",
            "required": false,
            "children": [
                {
                    "key": "name",
                    "type": "string",
                    "description": "Specification name",
                    "required": true
                },
                {
                    "key": "value",
                    "type": "string",
                    "description": "Specification value",
                    "required": true
                }
            ]
        },
        {
            "key": "inventory",
            "type": "object",
            "description": "Inventory information",
            "required": false,
            "children": [
                {
                    "key": "quantity",
                    "type": "int",
                    "description": "Available quantity",
                    "required": true
                },
                {
                    "key": "locations",
                    "type": "array",
                    "description": "Storage locations",
                    "required": false,
                    "children": [
                        {
                            "key": "warehouse",
                            "type": "string",
                            "description": "Warehouse identifier",
                            "required": true
                        },
                        {
                            "key": "stock",
                            "type": "int",
                            "description": "Stock at this location",
                            "required": true
                        }
                    ]
                }
            ]
        }
    ]
}
```

**Field Type Rules:**
- `string`: Text values, can include `enum_values` for validation
- `int`: Whole numbers only
- `float`: Decimal numbers
- `boolean`: true/false values
- `object`: Nested fields with `children`
- `array`: List of items with consistent structure defined in `children`

**Response:**
```json
{
    "schema_id": "e4563fe7-1e73-456e-a263-4799295546ce"
}
```

### 2. Extract Information (`POST /extract`)

Example using the comprehensive schema:

```json
POST /extract
{
    "text": "New MacBook Pro 2024 (SKU: MB2024PRO) in Electronics category. Premium laptop priced at $1,999.99 USD. Currently on sale! Specifications include: 16GB RAM, 1TB SSD. Available stock: 50 units total, distributed across warehouses: NYC-1 (30 units), LA-2 (20 units).",
    "schema_id": "e4563fe7-1e73-456e-a263-4799295546ce",
    "api_key": "sk-..."
}
```

**Response:**
```json
{
    "extracted_data": [
        {
            "basic_info": {
                "name": "MacBook Pro 2024",
                "sku": "MB2024PRO",
                "category": "Electronics"
            },
            "pricing": {
                "amount": 1999.99,
                "currency": "USD",
                "discounted": true
            },
            "specifications": [
                {
                    "name": "RAM",
                    "value": "16GB"
                },
                {
                    "name": "Storage",
                    "value": "1TB SSD"
                }
            ],
            "inventory": {
                "quantity": 50,
                "locations": [
                    {
                        "warehouse": "NYC-1",
                        "stock": 30
                    },
                    {
                        "warehouse": "LA-2",
                        "stock": 20
                    }
                ]
            }
        }
    ]
}
```

### 3. List Schemas (`GET /schemas`)

Lists all created schemas with metadata.

```bash
GET /schemas
```

**Response:**
```json
[
    {
        "id": "e4563fe7-1e73-456e-a263-4799295546ce",
        "name": "ComprehensiveProduct",
        "description": "Schema for extracting detailed product information",
        "created_at": "2024-03-10T14:30:00Z"
    }
]
```

### 4. Get Schema Details (`GET /schemas/{schema_id}`)

Retrieves detailed information about a specific schema.

```bash
GET /schemas/e4563fe7-1e73-456e-a263-4799295546ce
```

### 5. Delete Schema (`DELETE /schemas/{schema_id}`)

Removes a schema from the system.

```bash
DELETE /schemas/e4563fe7-1e73-456e-a263-4799295546ce
```

## 🔍 Field Type Details

| Type | Description | Validation | Example |
|------|-------------|------------|---------|
| string | Text values | Max length 100 chars | "Hello World" |
| int | Whole numbers | Must be integer | 42 |
| float | Decimal numbers | Must be numeric | 3.14 |
| boolean | True/False values | Must be true/false | true |
| object | Nested fields | Must have children | {"name": "John"} |
| array | List of items | Must have children template | [{"name": "RAM", "value": "16GB"}] |

## 🛠️ Error Handling

| Status Code | Meaning | Common Causes |
|------------|---------|---------------|
| 400 | Bad Request | Invalid schema structure, missing required fields |
| 401 | Unauthorized | Invalid or missing API key |
| 404 | Not Found | Schema ID doesn't exist |
| 429 | Too Many Requests | Exceeded OpenAI API rate limits |
| 500 | Server Error | Internal processing error |

## 📚 Dependencies

Key dependencies and their purposes:
```
fastapi          - Web framework
uvicorn         - ASGI server
pydantic        - Data validation
langchain       - AI integration
trustcall       - Schema extraction
python-multipart - File handling
```

## 🧪 Testing

```bash
# Run the application in debug mode
uvicorn app.main:app --reload --log-level debug
```

## 🔐 Security Notes

- Keep your `.env` file secure and never commit it
- API keys are validated for basic format (sk-... and length)
- Text input is limited to 10,000 characters
- Schema names are validated to prevent injection

Need help? Visit our [issues page](https://github.com/yourusername/schema-extractor/issues)
