from alibabacloud_fc20230330.client import Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials.models import Config
from alibabacloud_tea_openapi import models

from config.settings import (
    FC_ACCESS_KEY_ID,
    FC_ACCESS_KEY_SECRET,
    FC_ACCOUNT_ID,
    FC_REGION,
)

_client = None

def get_fc_client() -> Client:
    global _client
    if _client is None:
        credential = CredentialClient(
            Config(
                type="access_key",
                access_key_id=FC_ACCESS_KEY_ID,
                access_key_secret=FC_ACCESS_KEY_SECRET,  
            )    
        )
        _client = Client(
            models.Config(
                credential=credential,
                endpoint=f"{FC_ACCOUNT_ID}.{FC_REGION}.fc.aliyuncs.com",
            )
        )

    return _client