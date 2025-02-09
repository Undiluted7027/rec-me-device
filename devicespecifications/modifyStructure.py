import json

# Load the JSON file
with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Iterate over each brand and modify the devices structure
for brand in data["brands"]:
    updated_devices = []

    for device_name, device_info in brand["devices"].items():
        updated_devices.append(
            {"device_name": device_name, "link": device_info["link"]}
        )

    brand["devices"] = updated_devices  # Replace dictionary with list

# Save the modified JSON back to a file
output_file = "modified_data.json"
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)

print(f"JSON file updated successfully. Saved as '{output_file}'.")
