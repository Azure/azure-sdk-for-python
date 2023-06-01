from feature.management import FeatureManager, RandomFilter
import json

alpha_string = "{ \
	\"id\": \"Alpha\",\
	\"description\": \"\",\
	\"enabled\": true,\
	\"conditions\": {\
		\"client_filters\": []\
	}\
}"

beta_string = "{ \
	\"id\": \"Beta\",\
	\"description\": \"\",\
	\"enabled\": false,\
	\"conditions\": {\
		\"client_filters\": []\
	}\
}"

gamma_string = "{ \
	\"id\": \"Gamma\",\
	\"description\": \"\",\
	\"enabled\": true,\
	\"conditions\": {\
		\"client_filters\": [\
			{\
				\"name\": \"Microsoft.Random\",\
				\"parameters\": {\
					\"Value\": 50\
				}\
			}\
        ]\
	}\
}"

alpha_json = json.loads(alpha_string)
beta_json = json.loads(beta_string)
gamma_json = json.loads(gamma_string)
feature_flags = [alpha_json, beta_json, gamma_json]

feature_filters = {}
feature_filters["Microsoft.Random"] = RandomFilter()



feature_manager = FeatureManager(feature_flags, filters=feature_filters)

print("Alpha is ", feature_manager.is_enabled("Alpha"))
print("Beta is ", feature_manager.is_enabled("Beta"))
print("Gamma is ", feature_manager.is_enabled("Gamma"))
