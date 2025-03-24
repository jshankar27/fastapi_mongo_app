from fastapi import APIRouter
from app.models import ProductRequest
from app.database import (
    add_product_to_db,
    update_product_in_db,
    retrieve_products_from_db,
    retrieve_product_by_name_from_db,
    delete_product_by_name_from_db
)

router = APIRouter()

# create new product
@router.post("/")
async def create_product(product_request: ProductRequest):
    product_data = product_request.to_dict()
    return await add_product_to_db(product_data)


# update existing product
@router.put("/{product_name}")
async def update_product(product_name : str, product_request: ProductRequest):
    product_data = product_request.to_dict()
    return await update_product_in_db(product_name, product_data)


# retrieve all products
@router.get("/all")
async def get_all_products():
    return await retrieve_products_from_db()


# retrieve product by product name
@router.get("/{product_name}")
async def get_product_by_name(product_name):
    return await retrieve_product_by_name_from_db(product_name)


# delete exisitng product
@router.delete("/{product_name}")
async def delete_product_by_name(product_name):
    return await delete_product_by_name_from_db(product_name)