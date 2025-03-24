from motor import motor_asyncio
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError
from datetime import datetime, UTC
from fastapi.responses import JSONResponse
from app.models import SuccessResponse, ErrorResponse
import logging
from contextlib import asynccontextmanager
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGO_DETAILS = "mongodb://localhost:27017"
client = None
database = None
products_collection = None

async def connect_to_mongo(mongo_client=None, mongo_db=None):
    global client, database, products_collection
    try:
        # If we already have a client and database, don't reconnect
        if client and database:
            print("Database already connected, skipping connection")
            return
            
        if mongo_client:
            client = mongo_client
        else:
            client = motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
        
        if mongo_db:
            database = mongo_db
        else:
            database = client.products
            
        products_collection = database.get_collection("products_collection")
        # Ensure unique index on product field
        await products_collection.create_index("product", unique=True)
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

async def close_mongo_connection():
    global client
    if client:
        client.close()
        logging.info("MongoDB connection closed")


@asynccontextmanager
async def get_database():
    if not database:
        await connect_to_mongo()
    try:
        yield database
    finally:
        # Connection will be closed when the application shuts down
        pass

# Add a new product into to the database
async def add_product_to_db(product_data: dict) -> JSONResponse:
    product_data["created_at"] = datetime.now(UTC)
    try:
        product = await products_collection.find_one({"product": product_data["product"]})
        
        if(product):
            logging.debug(f"Product '{product_data['product']}' already exists.")
            return JSONResponse(
                status_code = 409, 
                content = ErrorResponse(message="Product already exists!").model_dump()
            )
            
        product = await products_collection.insert_one(product_data)
        return JSONResponse(
            status_code = 201, 
            content = SuccessResponse(
                message = f"Product '{product_data['product']}' is stored successfully!",
                data = product_helper(product.inserted_id, product_data)
            ).model_dump(exclude_none=True)
        )
    
    except PyMongoError as e:
        logging.debug(f"Database error while inserting product: {str(e)}")
        return build_internal_server_error_response()
    
    
# Update existing product into to the database
async def update_product_in_db(product_name: str, product_data: dict):
    product_data["updated_at"] = datetime.now(UTC)
    try:
        if(product_data["product"] == product_name):
            updated_product = await products_collection.find_one_and_update(
                {"product": product_name},
                {"$set": product_data})
        # Find the product by name
        existing_product = await products_collection.find_one({"product": product_data["product"]})
        if existing_product:
            return JSONResponse(
                status_code = 409, 
                content = ErrorResponse(message = f"Product already exists with the name {product_data["product"]}. Try updating with different name!").model_dump()
            )

        existing_product = await products_collection.find_one({"product": product_name})
        if not existing_product:
            return JSONResponse(
                status_code = 404, 
                content = ErrorResponse(message = f"Product does not exist!. Try creating the product in order to update.").model_dump()
            )
        # Update the product
        result = await products_collection.update_one(
            {"product": product_name},
            {"$set": product_data}
        )
        
        if result.modified_count == 0:
            return JSONResponse(
                status_code = 400, 
                content = ErrorResponse(message = "No update done to the Product!").model_dump()
            )
            
        # Get the updated product
        updated_product = await products_collection.find_one({"product": product_data["product"]})
        if updated_product:
            return JSONResponse(
                status_code = 200, 
                content = SuccessResponse(message = "Product updated successfully!", 
                                          data = product_helper(updated_product["_id"], updated_product)).model_dump()
            )
        else:
            return JSONResponse(
                status_code = 404, 
                content = ErrorResponse(message = "Product not found after update!").model_dump()
            )
            
    except Exception as e:
        logging.error(f"Error updating product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Retrieve all products from the database
async def retrieve_products_from_db() -> JSONResponse:
    try:
        cursor = products_collection.find()
        products = await cursor.to_list(length=None)
        
        if(products is None):
            return JSONResponse(
                status_code = 404, 
                content = ErrorResponse(message = "Product does not exists!").model_dump()
            )
            
        retrieved_products = []
        for product in products:
            retrieved_products.append(product_helper(product["_id"], product))
        return JSONResponse(
            status_code = 200, 
            content = SuccessResponse(
                data = retrieved_products
            ).model_dump(exclude_none=True)
        )
    
    except PyMongoError as e:
        logging.debug(f"Database error while retrieving all product: {str(e)}")
        return build_internal_server_error_response()
    
    
# Retrieve a product by name from the database
async def retrieve_product_by_name_from_db(product_name: str) -> JSONResponse:
    try:
        product = await products_collection.find_one({"product": product_name})
        
        if(product is None):
            logging.debug(f"Product '{product_name}' does not exist.")
            return JSONResponse(
                status_code = 404, 
                content = ErrorResponse(message = "Product does not exists! Please store the product in order to retrieve.").model_dump()
            )
        
        return JSONResponse(
            status_code = 200, 
            content = SuccessResponse(
                data = product_helper(product["_id"], product)
            ).model_dump(exclude_none=True)
        )

    except PyMongoError as e:
        logging.debug(f"Database error while retrieving product by name: {str(e)}")
        return ErrorResponse(message="Internal Server error, please try again later!")       
    
    
# Delete a product by name from the database
async def delete_product_by_name_from_db(product_name: str) -> JSONResponse:
    try:
        product = await products_collection.delete_one({"product": product_name})
        
        if(product.deleted_count == 1):
            return JSONResponse(
            status_code = 200, 
            content = SuccessResponse(
                message = f"Product '{product_name}' is deleted successfully!"
            ).model_dump(exclude_none=True)
        )
        
        logging.debug(f"Product '{product_name}' does not exist.")
        return JSONResponse(
                status_code = 404, 
                content = ErrorResponse(message = "Product does not exists! Please store the product in order to delete.").model_dump()
            )
    
    except PyMongoError as e:
        logging.debug(f"Database error while deleting product by name: {str(e)}")
        return build_internal_server_error_response()       
    
    
def product_helper(object_id, product) -> dict:
    print(product)
    return {
        "id": str(object_id),
        "product": product["product"],
        "unit": product["unit"],
        "description": product["description"],
        "price": product["price"]
    }
    
def build_internal_server_error_response():
    return JSONResponse(
            status_code = 500, 
            content = ErrorResponse(message="Internal Server error, please try again later!").model_dump()
        )    