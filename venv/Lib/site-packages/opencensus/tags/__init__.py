# Copyright 2018, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from opencensus.common.runtime_context import RuntimeContext
from opencensus.tags.tag import Tag
from opencensus.tags.tag_key import TagKey
from opencensus.tags.tag_value import TagValue
from opencensus.tags.tag_map import TagMap

__all__ = ['Tag', 'TagContext', 'TagKey', 'TagValue', 'TagMap']

TagContext = RuntimeContext.register_slot('tag_context', None)
