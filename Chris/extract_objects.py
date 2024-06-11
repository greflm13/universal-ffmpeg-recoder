import json

with open("possible.json", "r", encoding="utf-8") as f:
    objects = json.loads(f.read())
for obj in objects:
    with open("objects/" + str(hash(obj["format"]["filename"].replace("/", "_"))) + ".json", "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, indent=2))