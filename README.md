# Product API

A RESTful API built with FastAPI and MongoDB for managing products. This API provides asynchronous CRUD operations for products with proper error handling and data validation.

## Features

- Asynchronous operations using FastAPI and Motor (async MongoDB driver)
- CRUD operations for products
- Input validation using Pydantic models
- Proper error handling and status codes
- MongoDB integration with unique product names
- Comprehensive test suite with pytest
- Swagger UI documentation (available at `/docs`)

## Prerequisites

- Python 3.8+
- MongoDB running locally or a MongoDB Atlas connection string
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd product-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The API uses the following environment variables:
- `MONGO_DETAILS`: MongoDB connection string (default: "mongodb://localhost:27017")

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| POST | `/product/` | Create a new product |
| GET | `/product/all` | Get all products |
| GET | `/product/{product_name}` | Get a specific product by name |
| PUT | `/product/{product_name}` | Update a product |
| DELETE | `/product/{product_name}` | Delete a product |

### Request/Response Examples

#### Create Product
```http
POST /product/
Content-Type: application/json

{
    "product": "Sample Product",
    "unit": "piece",
    "description": "A sample product description",
    "price": 99.99
}
```

#### Update Product
```http
PUT /product/Sample Product
Content-Type: application/json

{
    "product": "Sample Product",
    "unit": "piece",
    "description": "Updated description",
    "price": 149.99
}
```

## Running Tests

The project includes a comprehensive test suite. To run the tests:

```bash
pytest tests/ -v
```

For verbose output with print statements:
```bash
pytest tests/ -v -s
```

## Project Structure

```
product-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── products.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_products.py
├── requirements.txt
└── README.md
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


# Starting virtual env
python3 -m venv venv

# Activating the virtual env
source venv/bin/activate

# Installing libraries
pip install -r requirements.txt

# Starting the app
python3 app/main.py

# Deactivating the virtual env
deactivate


# MONGO DB installation:
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

## to stop mongo services:
brew services stop mongodb-community

# Install mongo compass using homebrew
brew install --cask mongodb-compass