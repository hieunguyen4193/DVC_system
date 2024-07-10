import json
from pprint import pprint
import os
import time
import pandas as pd 
from datetime import datetime
import pathlib

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

import minio
from minio.error import S3Error
from minio.commonconfig import ENABLED
from minio.versioningconfig import VersioningConfig


class RDSBucket:
    def __init__(self, 
                 minio_credential, 
                 bucketName, 
                 PROFILE_NAME,
                 DATA_PROFILES,
                 es_credential, 
                 versioning = True, 
                 verbose = False):
        ##### minio client
        self.minio_credential = minio_credential
        self.es_credential = es_credential
        self.bucketName = bucketName
        self.PROFILE_NAME = PROFILE_NAME
        self.dataProfile = DATA_PROFILES[PROFILE_NAME]
        self.versioning = versioning
        self.verbose = verbose
        
        ##### elasticsearch client
        with open(self.es_credential, 'r') as file:
            keys = json.load(file)
            
        self.es = Elasticsearch(
            "http://localhost:9200", # deployed locally, no cloud
            basic_auth=(keys["username"], keys["password"])) 
        client_info = self.es.info()
        tmp = self.es.cat.indices(index='*', h='index', s='index:asc', format='json')
        self.all_ES_indices = [index['index'] for index in tmp if index['index'][0] != "."] # not show hidden indice
        
        if self.verbose:
            print('Connected to Elasticsearch!')
            pprint(client_info.body)
            
        ##### MAIN RUN
        with open(self.minio_credential, 'r') as file:
            keys = json.load(file)
        
        minio_client = minio.Minio(
            endpoint="localhost:9411",
            access_key=keys["accessKey"],
            secret_key=keys["secretKey"],
            secure=False 
        )
        self.minio_client = minio_client

    def list_objects_in_buckets(self):
            """
            Retrieves a list of objects in the bucket.

            Returns:
                A list of objects in the bucket.
            """
            return [item for item in self.minio_client.list_objects(self.bucketName, recursive=True)]
        
    def initBucket(self):
        ##### initialize a new bucket
        try:
            # Check if the bucket already exists
            exists = self.minio_client.bucket_exists(self.bucketName)
            if exists == False: 
                # Make a new bucket
                self.minio_client.make_bucket(self.bucketName)
                print(f"Bucket '{self.bucketName}' created successfully.")
                if self.versioning:
                    self.minio_client.set_bucket_versioning(self.bucketName, VersioningConfig(ENABLED))

            else:
                print(f"Bucket '{self.bucketName}' already exists. Cannot create bucket with the same name. Please choose another name")
            return True
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            return False
        
    def upload_file_to_bucket(self, path_to_file, object_name, file_metadata, update_version = True):
        """
        Uploads a file to the bucket.

        Args:
            path_to_file (str): The path to the file to be uploaded.
            object_name (str): The name of the object in the bucket.
            file_metadata (dict): Metadata associated with the file.
            update_version (bool, optional): Whether to update the version of the file if it already exists in the bucket. 
                Defaults to True.

        Returns:
            bool: True if the file was uploaded successfully, False otherwise.

        Raises:
            ValueError: If the file already exists in the bucket and update_version is set to False, or if the file metadata
                does not match the bucket's data profile.
        """
        ##### check if the object_name is already in the bucket. 
        if object_name in [item for item in self.minio_client.list_objects(self.bucketName, recursive=True)] == True and update_version == False:
            raise ValueError("Cannot upload file. The file already exists in the bucket. Please choose another name or set update_version = True")
        else:       
            ##### add bucket name to the file metadata
            file_metadata = {**file_metadata, **{"bucket": self.bucketName}}
            ##### check if the file_metadata match the bucket's dataProfile
            if sorted(list(file_metadata.keys())) == sorted([list(item.keys()) for item in self.dataProfile.values()][0]):
                try:
                    with open(path_to_file, 'rb') as file_data:
                        file_stat = os.stat(path_to_file)
                        put_object_res = self.minio_client.put_object(
                            bucket_name=self.bucketName,
                            object_name=object_name,
                            data=file_data,
                            length=file_stat.st_size,
                            metadata=file_metadata
                        )
                        
                    file_metadata = {**file_metadata, **{"versionID": put_object_res.version_id}}
                    if self.verbose:
                        print(f"File '{object_name}' uploaded successfully with metadata.")
                    
                    ##### if file upload successfully, add the metadata to the elasticsearch database
                    if self.bucketName in self.all_ES_indices == False:
                        self.es.indices.create(index = self.PROFILE_NAME,  mappings = self.dataProfile)
                    self.es.index(index = self.PROFILE_NAME, body = file_metadata)
                    return True
                except S3Error as e:
                    print(f"Error uploading file: {e}")
                    return False
            else:
                raise ValueError("Cannot upload file. The file metadata does not match the bucket's data profile")
            
    def download_file_from_bucket(self, object_name, downloaddir):
        """
        Downloads a file from the bucket.

        Args:
            object_name (str): The name of the object in the bucket.
            downloaddir (str): The directory to download the file to.

        Returns:
            bool: True if the file was downloaded successfully, False otherwise.
        """
        try:
            file_path = os.path.join(downloaddir, object_name)
            self.minio_client.fget_object(self.bucketName, object_name, file_path)
            print(f"File '{object_name}' downloaded successfully.")
            return True
        except S3Error as e:
            print(f"Error downloading file: {e}")
            return False
        
class ESearch:
    def __init__(self, 
                 es_credential, 
                 verbose = False):
        ##### minio client
        self.es_credential = es_credential
        self.verbose = verbose
        
        ##### elasticsearch client
        with open(self.es_credential, 'r') as file:
            keys = json.load(file)
            
        self.es = Elasticsearch(
            "http://localhost:9200", # deployed locally, no cloud
            basic_auth=(keys["username"], keys["password"])) 
        client_info = self.es.info()
        tmp = self.es.cat.indices(index='*', h='index', s='index:asc', format='json')
        self.ALL_PROFILES = [index['index'] for index in tmp if index['index'][0] != "."] # not show hidden indice
        
    def list_all_data_from_a_profile(self, PROFILE_NAME):
        query = {
            "query": {
                "match_all": {}
            }
        }
        response = self.es.search(index=PROFILE_NAME, body=query)
        indexdf = pd.DataFrame([doc['_source'] for doc in response['hits']['hits']])
        return(indexdf)
