
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta
import pytest
import base64
import asyncio
try:
    from unittest.mock import MagicMock, Mock, patch
except ImportError:  # python < 3.3
    from mock import MagicMock, Mock, patch 
from azure.communication.identity._shared.user_credential_async import CommunicationTokenCredential
import azure.communication.identity._shared.user_credential_async as user_credential_async
from azure.communication.identity._shared.utils import create_access_token
from azure.communication.identity._shared.utils import get_current_utc_as_int 
    
class TestCommunicationTokenCredential:
    
    @staticmethod
    def generate_token_with_custom_expiry(valid_for_seconds):
        expires_on = datetime.now() + timedelta(seconds=valid_for_seconds)
        expiry_json = '{"exp": ' + str(expires_on.timestamp()) + '}'
        base64expiry = base64.b64encode(
            expiry_json.encode('utf-8')).decode('utf-8').rstrip("=")
        token_template = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." +\
            base64expiry + ".adM-ddBZZlQ1WlN3pdPBOF5G4Wh9iZpxNP_fSvpF4cWs"
        return token_template
    
    @pytest.mark.asyncio
    async def test_raises_error_for_init_with_nonstring_token(self):
        with pytest.raises(TypeError) as err:
            credential = CommunicationTokenCredential(1234)
        assert str(err.value) == "token must be a string."
    
    @pytest.mark.asyncio
    async def test_raises_error_for_init_with_invalid_token(self):
        with pytest.raises(ValueError) as err:
            credential = CommunicationTokenCredential("not a token")
        assert str(err.value) == "Token is not formatted correctly"
    
    @pytest.mark.asyncio
    async def test_init_with_valid_token(self):
        initial_token = self.generate_token_with_custom_expiry(5 * 60)
        credential = CommunicationTokenCredential(initial_token)
        access_token = await credential.get_token()
        assert initial_token == access_token.token
    
    @pytest.mark.asyncio
    async def test_refresher_should_be_called_immediately_with_expired_token(self):
        refreshed_token = self.generate_token_with_custom_expiry(10 * 60)
        refresher = MagicMock(return_value=create_access_token(refreshed_token))
        expired_token = self.generate_token_with_custom_expiry(-(5 * 60))
        
        credential = CommunicationTokenCredential(expired_token, token_refresher=refresher)
        async with credential:
            access_token = await credential.get_token()
        
        refresher.assert_called_once()
        assert refreshed_token == access_token.token  
    
    @pytest.mark.asyncio
    async def test_refresher_should_not_be_called_before_expiring_time(self):
        initial_token = self.generate_token_with_custom_expiry(15 * 60)
        refreshed_token = self.generate_token_with_custom_expiry(10*60)
        refresher = MagicMock(return_value=create_access_token(refreshed_token))
        
        credential = CommunicationTokenCredential(initial_token, token_refresher=refresher, refresh_proactively=True)
        async with credential:
            access_token = await credential.get_token()
        
        refresher.assert_not_called()
        assert initial_token == access_token.token 
        
    @pytest.mark.asyncio
    async def test_refresher_should_not_be_called_when_token_still_valid(self):
        generated_token = self.generate_token_with_custom_expiry(15 * 60)
        new_token = self.generate_token_with_custom_expiry(10*60)
        refresher = MagicMock(return_value=create_access_token(new_token))
        
        credential = CommunicationTokenCredential(generated_token, token_refresher=refresher, refresh_proactively=False)
        async with credential:
            for i in range(10):
                access_token = await credential.get_token()
        
        refresher.assert_not_called()
        assert generated_token == access_token.token
        
    @pytest.mark.asyncio
    async def test_refresher_should_be_called_as_necessary(self):
        expired_token = self.generate_token_with_custom_expiry(-(10 * 60))
        refresher = MagicMock(return_value=create_access_token(expired_token))
        
        credential = CommunicationTokenCredential(expired_token, token_refresher=refresher)
        async with credential:
            access_token = await credential.get_token()
            access_token = await credential.get_token()
        
        assert refresher.call_count == 2
        assert expired_token == access_token.token  
        
    @pytest.mark.asyncio
    async def test_proactive_refresher_should_not_be_called_before_specified_time(self):
        refresh_minutes = 30
        token_validity_minutes = 60
        start_timestamp = get_current_utc_as_int()
        skip_to_timestamp = start_timestamp + (refresh_minutes - 5) * 60

        initial_token = self.generate_token_with_custom_expiry(token_validity_minutes * 60)
        refreshed_token = self.generate_token_with_custom_expiry(2 * token_validity_minutes * 60)
        refresher = MagicMock(return_value=create_access_token(refreshed_token))
        
        with patch(user_credential_async.__name__+'.get_current_utc_as_int', return_value=skip_to_timestamp):
            credential = CommunicationTokenCredential(
                initial_token,
                token_refresher=refresher,
                refresh_proactively=True,
                refresh_time_before_expiry=timedelta(minutes=refresh_minutes))
            async with credential:
                access_token = await credential.get_token() 

        assert refresher.call_count == 0
        assert access_token.token == initial_token
        # check that next refresh is always scheduled
        assert credential._timer is not None 
    
    @pytest.mark.asyncio
    async def test_proactive_refresher_should_be_called_after_specified_time(self):
        refresh_minutes = 30
        token_validity_minutes = 60
        start_timestamp = get_current_utc_as_int()
        skip_to_timestamp = start_timestamp + (refresh_minutes + 5) * 60

        initial_token = self.generate_token_with_custom_expiry(token_validity_minutes * 60)
        refreshed_token = self.generate_token_with_custom_expiry(2 * token_validity_minutes * 60)
        refresher = MagicMock(return_value=create_access_token(refreshed_token))
        
        with patch(user_credential_async.__name__+'.get_current_utc_as_int', return_value=skip_to_timestamp):
            credential = CommunicationTokenCredential(
                initial_token,
                token_refresher=refresher,
                refresh_proactively=True,
                refresh_time_before_expiry=timedelta(minutes=refresh_minutes))
            async with credential:
                access_token = await credential.get_token() 

        assert refresher.call_count == 1
        assert access_token.token == refreshed_token
        # check that next refresh is always scheduled
        assert credential._timer is not None 
     
              
    @pytest.mark.asyncio
    async def test_proactive_refresher_keeps_scheduling_again(self):
        refresh_seconds = 2
        expired_token = self.generate_token_with_custom_expiry(-5 * 60)
        first_refreshed_token = create_access_token(self.generate_token_with_custom_expiry(4))
        last_refreshed_token = create_access_token(self.generate_token_with_custom_expiry(10*60))
        refresher = MagicMock(side_effect=[first_refreshed_token, last_refreshed_token])
        
        credential = CommunicationTokenCredential(
                expired_token,
                token_refresher=refresher,
                refresh_proactively=True,
                refresh_time_before_expiry=timedelta(seconds=refresh_seconds))
        async with credential:
            await asyncio.sleep(4)
            access_token = await credential.get_token() 
           
        assert refresher.call_count == 2
        assert access_token.token == last_refreshed_token.token
        # check that next refresh is always scheduled
        assert credential._timer is not None
        
    @pytest.mark.asyncio
    async def test_exit_cancels_timer(self):
        refreshed_token = create_access_token(self.generate_token_with_custom_expiry(30*60))
        refresher = MagicMock(return_value=refreshed_token)
        expired_token = self.generate_token_with_custom_expiry(-10*60)
        
        credential = CommunicationTokenCredential(
                expired_token,
                token_refresher=refresher,
                refresh_proactively=True)
        credential._timer.cancel() 
        await asyncio.sleep(3)   
        assert refresher.call_count == 0