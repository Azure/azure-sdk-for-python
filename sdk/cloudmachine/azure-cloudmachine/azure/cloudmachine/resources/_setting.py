# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""Provide access to settings for globally used Azure configuration values.
"""
from typing import Callable, Optional, Dict, Union
import os

from azure.core.settings import _unset, _Unset, PrioritizedSetting, ValidInputType, ValueType

class StoredPrioritizedSetting(PrioritizedSetting):

    def __init__(
        self,
        name: str,
        *,
        to_str: Optional[Callable[[ValidInputType], str]] = None,
        env_var: Optional[str] = None,
        system_hook: Optional[Callable[[], ValidInputType]] = None,
        default: Union[ValidInputType, _Unset] = _unset,
        convert: Optional[Callable[[Union[ValidInputType, str]], ValueType]] = None,
    ):
        super().__init__(
            name=name,
            env_var=env_var,
            system_hook=system_hook,
            default=default,
            convert=convert
        )
        self._tostr = to_str or str


    def dump(
            self,
            *,
            read_env: bool = False,
            include_sensitive: bool = False
    ) -> Dict[str, str]:
        try:
            if self._user_value:
                return {self._name: self._tostr(self._user_value, include_sensitive)}
            if read_env and self.env_var and self.env_var in os.environ:
                return {self._name: self._tostr(os.environ[self.env_var], include_sensitive)}
            if not isinstance(self._default, (PrioritizedSetting, _Unset)):
                return {self._name: self._tostr(self._default, include_sensitive)}
        except RuntimeError:
            pass
        return {}
