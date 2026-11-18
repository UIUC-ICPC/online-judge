import os
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from datetime import datetime, timedelta, timezone
from urllib.parse import quote


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
