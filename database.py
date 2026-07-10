from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Read MongoDB URL from .env
MONGO_URL = os.getenv("MONGO_URL")
AI_SERVER_URL = os.getenv("AI_SERVER_URL")

# Create MongoDB client
client = AsyncIOMotorClient(MONGO_URL)

# Database
db = client["mindsense"]

# Collections
analysis_collection = db["analysis_results"]