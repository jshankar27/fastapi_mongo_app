# import pytest
# from httpx import ASGITransport, AsyncClient
# from contextlib import asynccontextmanager
# import pytest_asyncio
# from asgi_lifespan import LifespanManager
# from starlette.applications import Starlette
# from starlette.responses import PlainTextResponse
# from starlette.routing import Route

import json
import mongomock
from mongomock_motor import AsyncMongoMockClient
import pytest
from httpx import ASGITransport, AsyncClient, Response
from app.main import app
#from app.utils.httpx_wrapper import HttpxWrapper

# Global variable to store the product ID
created_product_id = None
created_product_description = None

pytestmark = pytest.mark.asyncio

async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Products API app!"}

async def test_create_product(client):
    global created_product_id, created_product_description
    from app.database import products_collection, database
    print(f"Using database: {database.name}") 
    product_data = {
        "product": "New Product",
        "unit": "piece",
        "description": "New Description",
        "price": 149.99
    }
    
    response = await client.post("/product/", json=product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["product"] == product_data["product"]
    assert data["data"]["price"] == "$149.9900"
    assert "id" in data["data"]
    
    created_product_id = data["data"]["id"]
    created_product_description = data["data"]["description"]
    
    created_product = await products_collection.find_one({"product": "New Product"})
    assert created_product is not None 

async def test_create_duplicate_product(client):
    product_data = {
        "product": "New Product",
        "unit": "piece",
        "description": "New Description",
        "price": 149.99
    }
    
    response = await client.post("/product/", json=product_data)
    assert response.status_code == 409
    assert "Product already exists!" in response.json()["message"]

async def test_get_all_products(client):
    response = await client.get("/product/all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1
    assert data["data"][0]["product"] == "New Product"
    assert data["data"][0]["id"] == created_product_id

async def test_get_product(client):
    global created_product_id
    response = await client.get(f"/product/New Product")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["product"] == "New Product"
    assert data["data"]["id"] == created_product_id

async def test_get_nonexistent_product(client):
    response = await client.get("/product/NonexistentProduct")
    assert response.status_code == 404
    assert "Product does not exists!" in response.json()["message"]

async def test_update_product(client):
    global created_product_id
    update_data = {
        "product": "New Product",
        "unit": "piece",
        "description": "Updated Description",
        "price": 199.99
    }
    
    response = await client.put(f"/product/New Product", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["product"] == update_data["product"]
    assert data["data"]["price"] == "$199.9900"
    assert data["data"]["description"] == update_data["description"]
    assert data["data"]["id"] == created_product_id

async def test_update_nonexistent_product(client):
    update_data = {
        "product": "NonexistentProduct",
        "unit": "piece",
        "description": "New Description",
        "price": 199.99
    }
    
    response = await client.put("/product/NonexistentProduct", json=update_data)
    assert response.status_code == 404
    assert "Product does not exists!" in response.json()["detail"]

async def test_delete_product(client):
    response = await client.delete("/product/New Product")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify product is deleted
    response = await client.get(f"/product/New Product")
    assert response.status_code == 404

async def test_delete_nonexistent_product(client):
    response = await client.delete("/product/NonexistentProduct")
    assert response.status_code == 404
    assert "Product does not exists!" in response.json()["message"]