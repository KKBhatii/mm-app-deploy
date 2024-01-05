import os
from google.cloud import storage
from google.oauth2 import service_account
import datetime

# Retrieve bucket name and credentials from environment variables
bucket_name = os.environ.get('GCS_BUCKET_NAME')
project_id = os.environ.get('GCS_PROJECT_ID')
client_email = os.environ.get('GCS_CLIENT_EMAIL')
client_id = os.environ.get('GCS_CLIENT_ID')
private_key = os.environ.get('GCS_PRIVATE_KEY')
private_key_id = os.environ.get('GCS_PRIVATE_KEY_ID')
client_cert_url= os.environ.get("GET_CERT_URL")

private_key = private_key.replace('\\n', '\n') if private_key else None

credentials_dict={
  "type": "service_account",
  "project_id": project_id,
  "private_key_id": private_key_id,
  "private_key": private_key,
  "client_email": client_email,
  "client_id": client_id,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": client_cert_url,
  "universe_domain": "googleapis.com"
}

credentials = service_account.Credentials.from_service_account_info(credentials_dict)
# Create storage client
storage_client = storage.Client(
    credentials=credentials
)

# Get bucket reference
bucket = storage_client.bucket(bucket_name)

def upload_file(file, destination_blob_name):
    """Uploads a file to the specified GCS bucket."""
    try:
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(file)
        return {'obj': blob}

    except Exception as e:
        return {'error': e}
    
    
def generate_signed_url(public_url,userProfile=False):
    def file_name(public_url,userProfile):
        if not userProfile:
            return f"listings/{str(public_url)[-20:]}"
        else:
            return f"profile_pictures/{str(public_url)[-20:]}"

    blob = bucket.blob(file_name(public_url=public_url,userProfile=userProfile))

    # Generate signed URL
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(hours=1),
        method="GET"
    )
    return signed_url

def delete_file(public_url, userProfile=False):
    def file_name(public_url, userProfile):
        if not userProfile:
            return f"listings/{str(public_url)[-20:]}"
        else:
            return f"profile_pictures/{str(public_url)[-20:]}"

    # Get the file name in the GCS bucket
    blob_name = file_name(public_url=public_url, userProfile=userProfile)

    # Delete the file from the bucket
    try:
        blob = bucket.blob(blob_name)
        blob.delete()
        return True
    except Exception as e:
        return False
