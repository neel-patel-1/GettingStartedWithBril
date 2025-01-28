import json


file_path = 'bril/test/parse/add.json'

with open(file_path, 'r') as file:
  data = json.load(file)

print(data)