import json
from jsonschema import validate


with open('config.json', 'r') as config_file:
	config = json.load(config_file)

jsonConfig = json.dumps(config)

schema = {
		"type" : "object",
		"properties" : {
			"botToken" : { "type": "string" },
			"TwitchAppClientID" : { "type": "string" },
			"TwitchAppClientSecret" : { "type": "string" },
		},
		 "required": ["botToken", "TwitchAppClientID", "TwitchAppClientSecret"],
}


validate(jsonConfig,schema)