from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from app.products import router as ProductRouter
from app.database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    await connect_to_mongo()
    yield
    # Shutdown: Close MongoDB connection
    await close_mongo_connection()
    
app = FastAPI(lifespan=lifespan)
app.include_router(ProductRouter, tags=['Products'], prefix='/product')

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Products API app!"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)