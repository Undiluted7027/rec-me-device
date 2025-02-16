import json
import uuid
from datetime import datetime, timezone
import os

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def preprocess_and_chunk(json_file, chunk_size=500, chunk_overlap=50):
    # Load the JSON data
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    # Iterate over each brand and its devices
    for brand in data.get("brands", []):
        brand_name = brand.get("brand_name", "Unknown Brand")

        for device in brand.get("devices", []):
            device_name = device.get("device_name", "Unknown Device")
            link = device.get("link", "")
            doc_id = str(uuid.uuid4())  # Unique identifier for this device record
            brief_specs = device.get("brief_specs", {})
            spec_detailed = device.get("spec_detailed", [])

            # Build a complete text representation for the device
            device_text = f"Brand: {brand_name}\nDevice: {device_name}\nLink: {link}\nDoc ID: {doc_id}\n\n"
            device_text += "Brief Specs:\n"
            for key, value in brief_specs.items():
                device_text += f"  {key}: {value}\n"
            device_text += "\nDetailed Specs:\n"

            # Process each detailed spec category separately to include category metadata.
            for category in spec_detailed:
                cat_name = category.get("category", "No Category")
                cat_desc = category.get("category_desc", "")
                # Add a marker for the start of a category section
                device_text += f"\nCategory: {cat_name}\nDescription: {cat_desc}\n"

                for sub in category.get("sub_categories", []):
                    sub_name = sub.get("sub_category", "No Sub-category")
                    sub_desc = sub.get("sub_category_desc", "")
                    device_text += (
                        f"  Sub-category: {sub_name}\n  Description: {sub_desc}\n"
                    )

                    for value_item in sub.get("values", []):
                        val = value_item.get("value", "")
                        unit = value_item.get("unit")
                        if unit:
                            device_text += f"    - {val} {unit}\n"
                        else:
                            device_text += f"    - {val}\n"

            # Now, split the full device text into chunks
            chunks = text_splitter.split_text(device_text)

            # Create a document for each chunk and attach rich metadata
            for i, chunk in enumerate(chunks):
                metadata = {
                    "doc_id": doc_id,
                    "brand": brand_name,
                    "device": device_name,
                    "link": link,
                    "chunk_index": i,
                    "text_length": len(chunk),
                    "source_file": json_file,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    # Optionally, you could try to detect and attach section metadata here.
                }
                documents.append(Document(page_content=chunk, metadata=metadata))

    return documents


# # Example usage:
# json_file_path = "partial_progress.json"  # Replace with your file path
# chunked_documents = preprocess_and_chunk(json_file_path)

# # Inspect one document chunk with its metadata:
# print("Chunk Content:\n", chunked_documents[0].page_content)
# print("Metadata:\n", chunked_documents[0].metadata)

# documents_data = [
#     {"page_content": doc.page_content, "metadata": doc.metadata}
#     for doc in chunked_documents
# ]

# # Save the list of dictionaries to a JSON file
# output_file = "chunked_documents.json"
# with open(output_file, "w", encoding="utf-8") as f:
#     json.dump(documents_data, f, indent=2, ensure_ascii=False)

# print(f"Saved {len(documents_data)} documents to {output_file}")


def setup_embedding_and_vector_store(docs):
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("imported embedding model")
    vector_store = FAISS.from_documents(docs, embedding_model)
    print("created vectors")
    vector_store.save_local("faiss_index_hf")
    return vector_store


def loadJSON(filename):
    data = {}
    with open(filename, "r", encoding="utf-8") as jsonFile:
        data = json.load(jsonFile)
    documents = [
        Document(page_content=item["page_content"], metadata=item["metadata"])
        for item in data
    ]
    return documents


# chunked_documents = loadJSON("chunked_documents.json")
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# vector_store = setup_embedding_and_vector_store(chunked_documents)
vector_store = FAISS.load_local(
    "faiss_index_hf", embedding_model, allow_dangerous_deserialization=True
)
query = "What is a tablet/ipad with a great battery life?"

# # # Retrieve the top k most similar chunks (e.g., top 4)
retrieved_docs = vector_store.similarity_search(query, k=4)

# # Print out the retrieved chunks along with their metadata
for idx, doc in enumerate(retrieved_docs):
    print(f"--- Result {idx+1} ---")
    print("Content:\n", doc.page_content)
    print("Metadata:\n", doc.metadata)
    print("\n")
