import json
import faiss
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
app = FastAPI()

# Load device specs
dataset = load_dataset("json", data_files="gsmarena_data.json")
devices = dataset["train"]
# print(dataset['train'][0])


def format_spec(device):
    specs = []
    for category in device["specifications"]:
        lst = device['specifications'][category]
        if lst is not None:
            for obj in lst:
                # print(f"{obj['name']}: {obj['value']}")
                specs.append(f"{obj['name']}: {obj['value']}")

        # specs.append(f"{device['specifications'][category][i]['name']}: {device['specifications'][category][i]['value']}")
    return "\n".join(specs)


device_texts = [format_spec(d) for d in devices]

device_embeddings = model.encode(device_texts, show_progress_bar=True)


# Create FAISS index
dimension = device_embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
faiss.normalize_L2(device_embeddings)
index.add(device_embeddings)

def search_devices(query, price_range=None, battery_min=None, k=5):
    # Semantic search
    query_embed = model.encode([query])
    D, I = index.search(query_embed, k)

    # Apply filters
    results = []
    for idx in I[0]:
        device = devices[idx]
        if price_range and not (price_range[0] <= device['price'] <= price_range[1]):
            continue
        if battery_min and device['battery'] < battery_min:
            continue
        results.append(device)

    return results[:k]

class Query(BaseModel):
    text: str
    max_price: float = None
    min_battery: int = None

@app.post("/search")
async def semantic_search(query: Query):
    return search_devices(
        query.text,
        price_range=(0, query.max_price) if query.max_price else None,
        battery_min=query.min_battery
    )

results = search_devices(
    "rugged phone with great battery life",
    price_range=(150, 300),
    battery_min=5000
)

print(results)
