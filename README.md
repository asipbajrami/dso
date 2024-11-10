# Dynamic Schema Extractor 🎯

A FastAPI service that helps you create custom schemas and extract structured information from text.

## 🚀 Quick Start

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## 📝 API Endpoints

### 1. Create Schema (`POST /schemas`)

Creates a new schema definition for information extraction.

```json
POST /schemas
{
    "name": "JobPosting",
    "description": "Schema for extracting job posting information",
    "fields": [
        {
            "key": "title",
            "type": "string",
            "description": "Job title",
            "required": true
        },
        {
            "key": "salary",
            "type": "object",
            "description": "Salary information",
            "required": false,
            "children": [
                {
                    "key": "amount",
                    "type": "int",
                    "description": "Salary amount",
                    "required": true
                },
                {
                    "key": "currency",
                    "type": "string",
                    "description": "Currency type",
                    "required": true,
                    "enum_values": ["USD", "EUR", "GBP"]
                }
            ]
        }
    ]
}
```

**Rules:**
- `name`: Must be a valid Python identifier (letters, numbers, underscores)
- `type`: Can be "string", "int", "boolean", "float", "object", or "array"
- Use `children` for nested objects and arrays
- Use `enum_values` to specify allowed values for a field

**Response:**
```json
{
    "schema_id": "e4563fe7-1e73-456e-a263-4799295546ce"
}
```

### 2. List Schemas (`GET /schemas`)

Returns all created schemas.

```bash
GET /schemas
```

**Response:**
```json
[
    {
        "id": "e4563fe7-1e73-456e-a263-4799295546ce",
        "name": "JobPosting",
        "description": "Schema for extracting job posting information",
        "created_at": "2024-03-10T14:30:00Z"
    }
]
```

### 3. Get Schema Details (`GET /schemas/{schema_id}`)

Retrieves a specific schema by ID.

```bash
GET /schemas/e4563fe7-1e73-456e-a263-4799295546ce
```

### 4. Delete Schema (`DELETE /schemas/{schema_id}`)

Deletes a specific schema.

```bash
DELETE /schemas/e4563fe7-1e73-456e-a263-4799295546ce
```

### 5. Extract Information (`POST /extract`)

Extracts structured information from text using a schema.

```json
POST /extract
{
    "text": "We're hiring a Senior Python Developer! Salary: $120,000/year. Must have 5+ years of experience.",
    "schema_id": "e4563fe7-1e73-456e-a263-4799295546ce",
    "api_key": "sk-..."  // Your OpenAI API key
}
```

Alternatively, you can provide fields directly:
```json
POST /extract
{
    "text": "We're hiring a Senior Python Developer!",
    "fields": [
        {
            "key": "position",
            "type": "string",
            "description": "Job position",
            "required": true
        }
    ],
    "api_key": "sk-..."
}
```

**Rules:**
- Either `schema_id` or `fields` must be provided
- `text` maximum length is 10,000 characters
- Valid OpenAI API key required

**Response:**
```json
{
    "extracted_data": [
        {
            "title": "Senior Python Developer",
            "salary": {
                "amount": 120000,
                "currency": "USD"
            }
        }
    ]
}
```

## 📊 Field Types

| Type | Description | Example |
|------|-------------|---------|
| string | Text values | "Hello World" |
| int | Whole numbers | 42 |
| float | Decimal numbers | 3.14 |
| boolean | True/False values | true |
| object | Nested fields | {"name": "John"} |
| array | List of items | [1, 2, 3] |

## 🛠️ Error Handling

Common error responses:

- `400`: Bad Request - Invalid input
- `401`: Unauthorized - Invalid API key
- `404`: Not Found - Schema not found
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Server Error - Internal error

## 🔑 Environment Variables

Create a `.env` file:
```
OPENAI_API_KEY=your-api-key
```
