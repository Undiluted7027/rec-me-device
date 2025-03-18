import json

with open("user-agents.json", "r", encoding="utf-8") as f:
    data = json.load(f)

lst = [dat['ua'] for dat in data]

print(lst)