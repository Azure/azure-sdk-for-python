from feature.management import FeatureManager, RandomFilter, TimeWindowFilter, TargetingFilter
import json

def build_feature_flag(name, enabled, client_filters):
	return "{{\"id\": \"{}\",\"description\": \"\",\"enabled\": \"{}\",\"conditions\": {{\"client_filters\": {}}}}}".format(name, enabled, client_filters)

def build_filter(name, parameters):
	return "{{\"name\": \"{}\",\"parameters\": {}}}".format(name, parameters)

alpha_string = build_feature_flag("Alpha", "true", "[]")
beta_string = build_feature_flag("Beta", "false", "[]")

gamma_string = build_feature_flag("Gamma", "true", "[" + build_filter("Microsoft.Random", "{\"Value\": 50}") + "]")
delta_string = build_feature_flag("Delta", "true", "[{\"name\": \"Microsoft.TimeWindowFilter\",\"parameters\": {\"Start\": \"Thu, 29 Jun 2023 07:00:00 GMT\",\"End\": \"Sat, 30 Jun 2023 07:00:00 GMT\"}}]")
sigma_string = build_feature_flag("Sigma", "true", "[{\"name\": \"Microsoft.TimeWindowFilter\",\"parameters\": {\"Start\": \"Tue, 27 Jun 2023 06:00:00 GMT\",\"End\": \"Wen, 28 Jun 2023 06:05:00 GMT\"}}]")
epsilon_string = build_feature_flag("Epsilon", "true", "[{\"name\": \"Microsoft.TimeWindowFilter\",\"parameters\": {\"Start\": \"Tue, 27 Jun 2023 06:00:00 GMT\"}}]")
zeta_string = build_feature_flag("Zeta", "true", "[{\"name\": \"Microsoft.TimeWindowFilter\",\"parameters\": {\"End\": \"Tue, 28 Jun 2024 06:00:00 GMT\"}}]")
target_string = build_feature_flag("Target", "true", "[{\"name\": \"Microsoft.Targeting\",\"parameters\": {\"Audience\": {\"Users\": [\"Adam\"],\"Groups\": [{\"Name\": \"Stage1\",\"RolloutPercentage\": 100}],\"DefaultRolloutPercentage\": 50,\"Exclusion\": {\"Users\": [],\"Groups\": []}}}}]")

feature_flags = {}

def build_feature_flags(name, string):
	json_object = json.loads(string)
	feature_flags[name] = json_object

build_feature_flags("Alpha", alpha_string)
build_feature_flags("Beta", beta_string)
build_feature_flags("Gamma", gamma_string)
build_feature_flags("Delta", delta_string)
build_feature_flags("Sigma", sigma_string)
build_feature_flags("Epsilon", epsilon_string)
build_feature_flags("Zeta", zeta_string)
build_feature_flags("Target", target_string)

feature_filters = {}
feature_filters["Microsoft.Random"] = RandomFilter()
feature_filters["Microsoft.TimeWindowFilter"] = TimeWindowFilter()
feature_filters["Microsoft.Targeting"] = TargetingFilter()



feature_manager = FeatureManager(feature_flags, filters=feature_filters)

print("Alpha is ", feature_manager.is_enabled("Alpha"))
print("Beta is ", feature_manager.is_enabled("Beta"))
print("Gamma is ", feature_manager.is_enabled("Gamma"))
print("Delta is ", feature_manager.is_enabled("Delta"))
print("Sigma is ", feature_manager.is_enabled("Sigma"))
print("Epsilon is ", feature_manager.is_enabled("Epsilon"))
print("Zeta is ", feature_manager.is_enabled("Zeta"))
print("Target is ", feature_manager.is_enabled("Target", user="Adam"))
print("Target is ", feature_manager.is_enabled("Target", user="Brian"))
