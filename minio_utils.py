#####-------------------------------------------------------------#####
##### FUNCTION TO CREATE A NEW BUCKET OF DATA IN MINIO 
#####-------------------------------------------------------------#####
import minio
from minio.error import S3Error

import pandas as pd
import os
import json
from minio.commonconfig import ENABLED
from minio.versioningconfig import VersioningConfig

def create_bucket(bucket_name, minio_credentials, versioning = True):
    """
    Create a bucket in MinIO.

    Parameters:
    - bucket_name (str): The name of the bucket to create.
    - minio_client (minio.Minio): An instance of the Minio client.

    Returns:
    - bool: True if the bucket was created successfully, False otherwise.
    """
    with open(minio_credentials, 'r') as file:
        keys = json.load(file)
        
    minio_client = minio.Minio(
        endpoint = "localhost:9000", # must use API port, not the original port
        access_key = keys["accessKey"],
        secret_key = keys["secretKey"],
        secure = False # FIX ME HIEU!!! WHAT IS THE BEST WAY TO HANDLE THIS SECURITY ISSUE?  
    )
    try:
        # Check if the bucket already exists
        exists = minio_client.bucket_exists(bucket_name)
        if exists == False: 
            # Make a new bucket
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
            if versioning:
                minio_client.set_bucket_versioning(bucket_name, VersioningConfig(ENABLED))

        else:
            print(f"Bucket '{bucket_name}' already exists.")
        return True
    except S3Error as e:
        print(f"Error creating bucket: {e}")
        return False

#####-------------------------------------------------------------#####
##### create a bucket with a pre-defined and fix template of metadata
#####-------------------------------------------------------------#####
def create_bucket_with_metadata_template(bucket_name, minio_credentials, profile, versioning = True):
    """
    Create a bucket in MinIO.

    Parameters:
    - bucket_name (str): The name of the bucket to create.
    - minio_client (minio.Minio): An instance of the Minio client.
    - profile: A metadata template. All data in the bucket must follow this metadata template. 
    The template is written in json format. 

    Returns:
    - bool: True if the bucket was created successfully, False otherwise.
    """
    with open(minio_credentials, 'r') as file:
        keys = json.load(file)
        
    minio_client = minio.Minio(
        endpoint = "localhost:9000", # must use API port, not the original port
        access_key = keys["accessKey"],
        secret_key = keys["secretKey"],
        secure = False # FIX ME HIEU!!! WHAT IS THE BEST WAY TO HANDLE THIS SECURITY ISSUE?  
    )
    try:
        # Check if the bucket already exists
        exists = minio_client.bucket_exists(bucket_name)
        if exists == False: 
            # Make a new bucket
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
            if versioning:
                minio_client.set_bucket_versioning(bucket_name, VersioningConfig(ENABLED))

        else:
            print(f"Bucket '{bucket_name}' already exists.")
        return True
    except S3Error as e:
        print(f"Error creating bucket: {e}")
        return False

#####-------------------------------------------------------------#####
##### Upload file with metadata
#####-------------------------------------------------------------#####
def upload_file_with_metadata(bucket_name, 
                              object_name, 
                              file_to_upload, 
                              metadata, 
                              minio_credentials,
                              verbose = False):
    """
    Upload a file to a MinIO bucket with specified metadata.

    Parameters:
    - bucket_name (str): The name of the target bucket.
    - object_name (str): The object name in the bucket.
    - file_to_upload (str): The local path to the file to be uploaded.
    - metadata (dict): A dictionary of metadata to attach to the object.
    - minio_credentials (str): Path to the JSON file with MinIO credentials.

    Returns:
    - bool: True if the file was uploaded successfully, False otherwise.
    """
    with open(minio_credentials, 'r') as file:
        keys = json.load(file)
    
    minio_client = minio.Minio(
        endpoint="localhost:9000",
        access_key=keys["accessKey"],
        secret_key=keys["secretKey"],
        secure=False 
    )
    
    try:
        with open(file_to_upload, 'rb') as file_data:
            file_stat = os.stat(file_to_upload)
            minio_client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_stat.st_size,
                metadata=metadata
            )
        if verbose:
            print(f"File '{object_name}' uploaded successfully with metadata.")
        return True
    except S3Error as e:
        print(f"Error uploading file: {e}")
        return False
    
#####-------------------------------------------------------------#####
##### Extract all metadata from a bucket in minio
#####-------------------------------------------------------------#####
def extract_metadata_of_all_objects(bucket_name, minio_credentials, simplified = False):
    """
    Extract metadata of all objects in a specified MinIO bucket.

    Parameters:
    - bucket_name (str): The name of the MinIO bucket.
    - minio_credentials (str): Path to the JSON file with MinIO credentials.

    Returns:
    - dict: A dictionary with object names as keys and their metadata as values.
    """
    with open(minio_credentials, 'r') as file:
        keys = json.load(file)
    
    minio_client = minio.Minio(
        endpoint="localhost:9000",
        access_key=keys["accessKey"],
        secret_key=keys["secretKey"],
        secure=False  # Consider using secure=True in production environments
    )
    
    metadata_dict = {}
    try:
        objects = minio_client.list_objects(bucket_name, recursive=True, include_version = True)
        for obj in objects:
            obj_info = minio_client.stat_object(bucket_name, obj.object_name)
            metadata_dict[obj.object_name] = obj_info.metadata
        print("Metadata extracted successfully.")
        metadatadf = pd.DataFrame.from_dict(metadata_dict, orient = "index").reset_index()
        if simplified == True:
            metadatadf = metadatadf[["index", "x-amz-version-id"] + [item for item in metadatadf.columns if "x-amz-meta-" in item]]
            metadatadf.columns = [item.replace("x-amz-meta-", "") for item in metadatadf.columns]
        return metadatadf
    except S3Error as e:
        print(f"Error extracting metadata: {e}")
        return {}

#####-------------------------------------------------------------#####
# Search across different buckets in the minio server
#####-------------------------------------------------------------#####
def search_across_buckets(search_criteria, minio_credentials):
    # Load MinIO credentials
    with open(minio_credentials, 'r') as file:
        keys = json.load(file)
    
    # Initialize MinIO client
    minio_client = minio.Minio(
        keys['endpoint'],
        access_key=keys['access_key'],
        secret_key=keys['secret_key'],
        secure=keys['secure']
    )
    
    # List all buckets
    buckets = minio_client.list_buckets()
    
    # Initialize a dictionary to hold search results
    search_results = {}
    
    # Iterate through each bucket
    for bucket in buckets:
        bucket_name = bucket.name
        # List or search objects in the bucket
        # >>> TO ADD: list and search data by metadata of the bucket?