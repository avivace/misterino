import json
from jsonschema import validate


with open('configSchema.json', 'r') as configSchemaFile:
	configSchema = json.load(configSchemaFile)

with open('config.json', 'r') as configFile:
	config = json.load(configFile)

validate(config, configSchema)