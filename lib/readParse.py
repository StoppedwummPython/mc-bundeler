import json
def read_and_parse(dir: str):
    global content
    content = ""
    with open(dir, "r") as f:
        content = f.read()
    return json.loads(content)