# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# The idea was to send a newsletter to partner as a table checklist. Each line is a service, each columnd is a requirement (mypy, samples, etc.)
# To make it easier for people to see "what is my status". We could put different colors depending on status criticality (red if you're a month away from being blocked, warning if you have work to do but you have time, etc.)
# And I would want the status email to have a red warning like "CI disabled for lack of compliance" of something like that.
# If we script the generation of that table in MD, we can copy past it straight in an email, I wouldn't want anyone to manually have to write that table

import argparse

