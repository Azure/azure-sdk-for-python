# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This code violates client-method-name-no-double-underscore

class Some1Client():
    @staticmethod
    async def __create_configuration():
        pass

    @staticmethod
    async def __get_thing():
        pass

    @staticmethod
    async def __list_thing():
        pass