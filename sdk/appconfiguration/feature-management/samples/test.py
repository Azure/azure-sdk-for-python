from feature.management import FeatureManager
from randomfilter import RandomFilter
import json
import os
import sys

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

f = open(script_directory + "/formatted-feature-flags.json", "r")

feature_flags = json.load(f)

feature_manager = FeatureManager(feature_flags, feature_filters={"Microsoft.Random": RandomFilter()})

# Is always true
print("Alpha is ", feature_manager.is_enabled("Alpha"))
# Is always false
print("Beta is ", feature_manager.is_enabled("Beta"))
# Is false 50% of the time
print("Gamma is ", feature_manager.is_enabled("Gamma"))
# Is true between 06-29-2023 to 07-17-2023
print("Delta is ", feature_manager.is_enabled("Delta"))
# Is true After 06-27-2023
print("Sigma is ", feature_manager.is_enabled("Sigma"))
# Is true Before 06-28-2023
print("Epsilon is ", feature_manager.is_enabled("Epsilon"))
print("Zeta is ", feature_manager.is_enabled("Zeta"))
# Target is true for Adam, group Stage 1, and 50% of users
print("Target is ", feature_manager.is_enabled("Target", user="Adam"))
print("Target is ", feature_manager.is_enabled("Target", user="Brian"))
