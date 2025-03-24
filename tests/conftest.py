import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient
from asgi_lifespan import LifespanManager
from app.main import app
from app.database import connect_to_mongo, close_mongo_connection, products_collection, get_database, database, client
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add this to ensure pytest-asyncio is properly configured
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
def test_app():
    return app

@pytest_asyncio.fixture
async def client():
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://test"
        ) as ac:
            yield ac

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    print("\n=== Starting setup_test_db fixture ===")  # Using print for immediate visibility
    logger.debug("Starting setup_test_db fixture")
    
    # Create a mock MongoDB client
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client.test_db
    print(f"Created mock database: {mock_db.name}")  # Using print for immediate visibility
    logger.debug(f"Created mock database: {mock_db.name}")
    
    # Override the database connection and get_database function
    app.dependency_overrides[connect_to_mongo] = lambda: mock_db
    app.dependency_overrides[get_database] = lambda: mock_db
    print("Overridden database connection functions")  # Using print for immediate visibility
    logger.debug("Overridden database connection functions")
    
    # Override the products collection to use test database
    global products_collection, database, client
    old_collection = products_collection
    products_collection = mock_db.products
    database = mock_db
    client = mock_client
    print(f"Overridden products_collection. Old: {old_collection}, New: {products_collection}")  # Using print for immediate visibility
    logger.debug(f"Overridden products_collection. Old: {old_collection}, New: {products_collection}")
    
    # Connect to test database
    print("Attempting to connect to test database")  # Using print for immediate visibility
    logger.debug("Attempting to connect to test database")
    try:
        # Pass both mock client and mock database to connect_to_mongo
        await connect_to_mongo(mongo_client=mock_client, mongo_db=mock_db)
        print("Successfully connected to test database")  # Using print for immediate visibility
        logger.debug("Successfully connected to test database")
        print(f"Current database name: {database.name if database else 'None'}")
    except Exception as e:
        print(f"Error connecting to test database: {str(e)}")  # Using print for immediate visibility
        logger.error(f"Error connecting to test database: {str(e)}")
        raise
    
    # Verify the connection
    try:
        # Try to insert a test document
        test_doc = {"test": "connection"}
        result = await mock_db.test_collection.insert_one(test_doc)
        print(f"Test document inserted with ID: {result.inserted_id}")  # Using print for immediate visibility
        logger.debug(f"Test document inserted with ID: {result.inserted_id}")
        
        # Try to retrieve it
        retrieved = await mock_db.test_collection.find_one({"test": "connection"})
        print(f"Retrieved test document: {retrieved}")  # Using print for immediate visibility
        logger.debug(f"Retrieved test document: {retrieved}")
        
        # Clean up test document
        await mock_db.test_collection.delete_one({"test": "connection"})
        print("Cleaned up test document")  # Using print for immediate visibility
        logger.debug("Cleaned up test document")
    except Exception as e:
        print(f"Error verifying database connection: {str(e)}")  # Using print for immediate visibility
        logger.error(f"Error verifying database connection: {str(e)}")
        raise
    
    yield
    
    # Cleanup after tests
    print("Starting cleanup")  # Using print for immediate visibility
    logger.debug("Starting cleanup")
    try:
        await close_mongo_connection()
        print("Successfully closed database connection")  # Using print for immediate visibility
        logger.debug("Successfully closed database connection")
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")  # Using print for immediate visibility
        logger.error(f"Error during cleanup: {str(e)}")
        raise
    print("=== Completed setup_test_db fixture ===\n")  # Using print for immediate visibility

@pytest_asyncio.fixture
async def test_product():
    print("\n=== Creating test product ===")  # Using print for immediate visibility
    logger.debug("Creating test product")
    product = {
        "product": "Test Product",
        "unit": "piece",
        "description": "Test Description",
        "price": 99.99
    }
    try:
        result = await products_collection.insert_one(product)
        product["_id"] = result.inserted_id
        print(f"Test product created with ID: {result.inserted_id}")  # Using print for immediate visibility
        logger.debug(f"Test product created with ID: {result.inserted_id}")
        return product
    except Exception as e:
        print(f"Error creating test product: {str(e)}")  # Using print for immediate visibility
        logger.error(f"Error creating test product: {str(e)}")
        raise 
