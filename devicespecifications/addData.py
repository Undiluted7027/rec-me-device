from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import json
from typing import Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceSpecsDB:
    def __init__(self, connection_string: str):
        """
        Initialize MongoDB connection and setup collections

        Args:
            connection_string: MongoDB connection string
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client["device_specifications"]

            # Create collections
            self.brands = self.db["brands"]
            self.devices = self.db["devices"]
            self.categories = self.db["categories"]

            # Create indexes
            self._setup_indexes()

            logger.info("Successfully connected to MongoDB")

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def _setup_indexes(self):
        """Setup necessary indexes for optimal querying"""
        # Brands collection indexes
        self.brands.create_index("brand_name", unique=True)

        # Devices collection indexes
        self.devices.create_index("brand_id")
        self.devices.create_index("device_name")
        self.devices.create_index([("brand_id", 1), ("device_name", 1)], unique=True)

        # Categories collection indexes
        self.categories.create_index([("device_id", 1), ("category", 1)])

    def insert_brand(self, brand_data: Dict[str, Any]) -> str:
        """
        Insert brand information into the brands collection

        Args:
            brand_data: Dictionary containing brand information

        Returns:
            Inserted brand ID
        """
        brand_doc = {"brand_name": brand_data["brand_name"], "url": brand_data["url"]}

        result = self.brands.insert_one(brand_doc)
        return result.inserted_id

    def insert_device(self, brand_id: str, device_data: Dict[str, Any]) -> str:
        """
        Insert device information into the devices collection

        Args:
            brand_id: Reference to the brand
            device_data: Dictionary containing device information

        Returns:
            Inserted device ID
        """
        device_doc = {
            "brand_id": brand_id,
            "device_name": device_data["device_name"],
            "link": device_data.get("link"),
            "brief_specs": device_data.get("brief_specs", {}),
        }

        result = self.devices.insert_one(device_doc)
        return result.inserted_id

    def insert_categories(self, device_id: str, spec_detailed: List[Dict[str, Any]]):
        """
        Insert detailed specifications into the categories collection

        Args:
            device_id: Reference to the device
            spec_detailed: List of detailed specifications
        """
        category_docs = []

        for category in spec_detailed:
            category_doc = {
                "device_id": device_id,
                "category": category["category"],
                "category_desc": category["category_desc"],
                "sub_categories": category["sub_categories"],
            }
            category_docs.append(category_doc)

        if category_docs:
            self.categories.insert_many(category_docs)


def import_device_specs(file_path: str, connection_string: str):
    """
    Import device specifications from JSON file into MongoDB

    Args:
        file_path: Path to the JSON file
        connection_string: MongoDB connection string
    """
    try:
        # Initialize database
        db = DeviceSpecsDB(connection_string)

        # Load JSON data
        with open(file_path, "r") as f:
            data = json.load(f)

        # Insert brand
        for brand in data["brands"]:
            print(brand)
            brand_id = db.insert_brand(brand)

            # Insert devices and their specifications
            for device in brand["devices"]:
                device_id = db.insert_device(brand_id, device)

                if "spec_detailed" in device:
                    db.insert_categories(device_id, device["spec_detailed"])

        logger.info("Successfully imported device specifications")

    except Exception as e:
        logger.error(f"Error importing device specifications: {e}")
        raise


# Example schema validation rules
schema_validation = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["brand_id", "device_name"],
            "properties": {
                "brand_id": {
                    "bsonType": "objectId",
                    "description": "Reference to the brand document",
                },
                "device_name": {
                    "bsonType": "string",
                    "description": "Name of the device",
                },
                "brief_specs": {
                    "bsonType": "object",
                    "properties": {
                        "SoC": {"bsonType": "string"},
                        "CPU": {"bsonType": "string"},
                        "RAM": {"bsonType": "string"},
                        "Storage": {"bsonType": "string"},
                        "Display": {"bsonType": "string"},
                        "Battery": {"bsonType": "string"},
                        "OS": {"bsonType": "string"},
                    },
                },
            },
        }
    }
}

# Example usage
if __name__ == "__main__":
    # Replace with your MongoDB connection string
    MONGO_URI = "mongodb://localhost:27017/"

    # Import data
    import_device_specs("partial_progress.json", MONGO_URI)
