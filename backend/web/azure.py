import os
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from functools import cache

"""
TODO: there r the a few options for fetching from blob
1. 1 single problems container 
    -> fetch directly, unzip and return statement (potentially cache)
2. generate read-only sas urls so clients and fetch statements directly
    from blob storage 
3. 2 separate but synced containers w one containing statements
    -> fetch from the statements container
(not sure which to use)
"""
# @cache
# def get_azure_client():
#     ACCOUNT = os.environ["AZURE_ACCOUNT"]
#     CONTAINER = os.environ["AZURE_CONTAINER"]
#     SAS = os.environ["AZURE_SAS"]

#     URL = f"https://{ACCOUNT}.blob.core.windows.net/{CONTAINER}?{SAS}"
#     client = ContainerClient.from_container_url(container_url=URL)
#     return client


# def get_problem_statement(problem_path):
#     client = get_azure_client()
#     blob = client.get_blob_client(problem_path)
#     download = blob.download_blob()

#     content_type = download.properties.content_settings.content_type
#     statement = download.readall()

#     return statement, content_type


def get_blob_sas_url(blob_name):
    ACCOUNT = os.environ["AZURE_ACCOUNT"]
    CONTAINER = os.environ["AZURE_CONTAINER"]
    KEY = os.environ["AZURE_STORAGE_KEY"]

    token = generate_blob_sas(
        account_name=ACCOUNT,
        container_name=CONTAINER,
        blob_name=blob_name,
        account_key=KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(minutes=60),
        protocol="https",
        content_disposition="inline",
    )

    BASE = f"https://{ACCOUNT}.blob.core.windows.net/"
    END = f"{quote(CONTAINER)}/{quote(blob_name)}?{token}"
    return BASE + END
