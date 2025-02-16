import json, re
from collections import defaultdict


def analyze_spec_field(value):
    if isinstance(value, list):
        return {"type": "nested_list", "description": "Contains sub-specifications"}

    value = str(value).strip()

    # Common patterns
    patterns = [
        (r"^\d+\s*GB?\s*RAM?$", "storage_unit", "RAM size with unit"),
        (r"^\d+\s*(MP|Mp|mp|megapixel)", "camera_spec", "Camera resolution"),
        (r"\d+\s*(mAh|MAh|mah)", "battery_capacity", "Battery capacity"),
        (r"\d+\.?\d*\s*(g|oz)", "weight", "Weight measurement"),
        (r"\d+\s*(EUR|USD|\$|£|€)", "price", "Currency value"),
        (r"\d+\.?\d*\s*(mm|in)", "dimension", "Physical dimension"),
        (r"\d+x\d+\s*pixels", "resolution", "Screen resolution"),
        (r"\d+\s*cm\d+", "screen_area", "Screen area measurement"),
        (r"Yes|No|Unknown", "boolean_like", "Yes/No values"),
        (r"\d{4}", "year", "4-digit year"),
        (r"About \d+", "approximate_value", "Approximate numerical value"),
        (r"\d+\s*GB", "storage_size", "Storage capacity"),
        (r"\d+\+?\s*GB", "storage_variant", "Storage variants with '+'"),
        (r"\d+\s*h", "time_duration", "Time duration in hours"),
        (r"[\d\.]+\s*GHz", "clock_speed", "Processor speed"),
        (r"\d+\s*nm", "chip_process", "Chip manufacturing process"),
        (r"^[\d\.]+$", "pure_number", "Numerical value without units"),
        (r"^\d+\s*°", "angle", "Camera/viewing angle"),
        (r"^[-\.\d\s/x]+$", "fraction_number", "Number with fractions"),
    ]

    for pattern, type_name, desc in patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return {"type": type_name, "description": desc}

    if any(c.isdigit() for c in value):
        return {"type": "mixed_numeric", "description": "Contains numbers and text"}

    return {"type": "text", "description": "General text field"}


# Main analysis
spec_analysis = defaultdict(
    lambda: {"count": 0, "types": defaultdict(lambda: {"count": 0, "examples": set()})}
)

data = {}
with open("gsmarena_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# print(data[0])

for device in data:  # Assuming data contains your JSON
    for category in device["specifications"]:
        for spec in device["specifications"][category]:
            key = f"{category} › {spec['name']}"  # Hierarchical key
            value = str(spec["value"])

            analysis = analyze_spec_field(value)
            spec_analysis[key]["count"] += 1
            spec_type = analysis["type"]

            spec_analysis[key]["types"][spec_type]["count"] += 1
            spec_analysis[key]["types"][spec_type]["examples"].add(
                value[:50]
            )  # Store truncated examples

# Convert sets to lists for JSON serialization
for key in spec_analysis:
    for t in spec_analysis[key]["types"]:
        spec_analysis[key]["types"][t]["examples"] = list(
            spec_analysis[key]["types"][t]["examples"]
        )[:5]

# Save to file
with open("spec_analysis.json", "w") as f:
    json.dump(spec_analysis, f, indent=2)
