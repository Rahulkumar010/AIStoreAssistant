"""
Script to seed initial stores into ChromaDB
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from chromadb_client import chromadb
from database_models import Store


async def seed_stores():
    """Seed initial stores"""
    stores_data = [
        {
            "Store ID": "STR001",
            "Full Address": "123 London Bridge, London",
            "Geo Location ID": "LON001",
            "store_images": "/app/new_app/Inputs/Images/Store 1",
            "store_videos": "/app/new_app/Inputs/Videos"
        },
        {
            "Store ID": "STR002",
            "Full Address": "456 Manchester Central, Manchester",
            "Geo Location ID": "MAN001",
            "store_images": "/app/new_app/Inputs/Images/Store 2",
            "store_videos": "/app/new_app/Inputs/Videos"
        },
        {
            "Store ID": "STR003",
            "Full Address": "789 Birmingham High Street, Birmingham",
            "Geo Location ID": "BIR001",
            "store_images": "/app/new_app/Inputs/Images/Store 3",
            "store_videos": "/app/new_app/Inputs/Videos"
        },
        {
            "Store ID": "STR004",
            "Full Address": "321 Edinburgh Royal Mile, Edinburgh",
            "Geo Location ID": "EDI001",
            "store_images": "/app/new_app/Inputs/Images/Store 4",
            "store_videos": "/app/new_app/Inputs/Videos"
        },
        {
            "Store ID": "STR005",
            "Full Address": "654 Bristol City Centre, Bristol",
            "Geo Location ID": "BRI001",
            "store_images": "/app/new_app/Inputs/Images/Store 5",
            "store_videos": "/app/new_app/Inputs/Videos"
        }
    ]
    
    print("Seeding stores...")
    for store_data in stores_data:
        try:
            store = Store(**store_data)
            await chromadb.create_store(store)
            print(f"✓ Created store: {store_data['Store ID']} - {store_data['Full Address']}")
        except Exception as e:
            print(f"✗ Error creating store {store_data['Store ID']}: {str(e)}")
    
    # Verify stores
    stores = await chromadb.get_all_stores()
    print(f"\n✓ Total stores in database: {len(stores)}")
    for store in stores:
        print(f"  - {store.store_id}: {store.full_address}")


if __name__ == "__main__":
    asyncio.run(seed_stores())
