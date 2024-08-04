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
#
def object_exists_in_bucket(minio_client, bucket_name, object_name):
    """
    Check if an object exists in a MinIO bucket.

    Args:
        minio_client (Minio): The MinIO client.
        bucket_name (str): The name of the bucket.
        object_name (str): The name of the object to check.

    Returns:
        bool: True if the object exists, False otherwise.
    """
    try:
        # Attempt to get object's metadata
        minio_client.stat_object(bucket_name, object_name)
        return True  # If the above line succeeds, the object exists
    except Exception as e:
        # If an exception is caught, the object does not exist
        return False

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
    
        
    def upload_file_to_bucket(self, path_to_file, object_name, file_metadata, update_version = False, raise_error_if_exists = True):
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
        # if (object_name in [item.object_name for item in self.minio_client.list_objects(self.bucketName, recursive=True)]) == True and (update_version == False):
        if (object_exists_in_bucket(self.minio_client, self.bucketName, object_name) == True) and (update_version == False):
            if raise_error_if_exists:
                print("{} is already existed".format(object_name))
                raise ValueError("Cannot upload file. The file already exists in the bucket. Please choose another name or set update_version = True")
            else:
                print("The object is already existed. Skip uploading")
                # pass
        else:       
            ##### add bucket name to the file metadata
            file_metadata = {**file_metadata, **{"bucket": self.bucketName}}
            ##### check if the file_metadata match the bucket's dataProfile
            if sorted(list(file_metadata.keys())) == sorted([list(item.keys()) for item in self.dataProfile.values()][0]):
                try:
                    file_metadata = {**file_metadata, **{"profileName": self.PROFILE_NAME}}
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
                print([item for item in sorted(list(file_metadata.keys())) if item not in sorted([list(item.keys()) for item in self.dataProfile.values()][0])])
                
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
    
    #####----------------------------------------------------------------#####
    ##### UPDATE ME: new features and functions
    #####----------------------------------------------------------------#####
    # def update_metadata(self):

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
            basic_auth=(
                keys["username"], 
                keys["password"])
            ) 
        client_info = self.es.info()
        tmp = self.es.cat.indices(index='*', h='index', s='index:asc', format='json')
        self.ALL_PROFILES = [index['index'] for index in tmp if index['index'][0] != "."] # not show hidden indice
        
    def list_all_data_from_a_profile(self, PROFILE_NAME):
        query = {
            "query": {
                "match_all": {}
            }
        }
        response = self.es.search(index=PROFILE_NAME, body=query, size = self.es.count(index=PROFILE_NAME)['count'])
        indexdf = pd.DataFrame([doc['_source'] for doc in response['hits']['hits']])
        return(indexdf)
    
    def search(self, search_indices, search_query, size = 100):
        response = self.es.search(index = search_indices, body = search_query, size = size)
        search_resdf = pd.DataFrame([doc['_source'] for doc in response['hits']['hits']])
        return(search_resdf)

    def search_scroll(self, search_indices, search_query):
        # Initialize the scroll
        response = self.es.search(index=search_indices, body=search_query, scroll='2m')
        scroll_id = response['_scroll_id']
        all_hits = response['hits']['hits']
        
        # Scroll through the results
        while True:
            response = self.es.scroll(scroll_id=scroll_id, scroll='2m')
            hits = response['hits']['hits']
            if not hits:
                break
            all_hits.extend(hits)
        
        # Collect all results
        search_resdf = pd.DataFrame([doc['_source'] for doc in all_hits])
        return search_resdf
    
    def scroll_all_data_from_a_profile(self, PROFILE_NAME):
        query = {
            "query": {
                "match_all": {}
            }
        }
        # Initialize the scroll
        response = self.es.search(index=PROFILE_NAME, body=query, scroll='2m', size=1000)
        scroll_id = response['_scroll_id']
        all_hits = response['hits']['hits']
        
        # Scroll through the results
        while True:
            response = self.es.scroll(scroll_id=scroll_id, scroll='2m')
            hits = response['hits']['hits']
            if not hits:
                break
            all_hits.extend(hits)
        
        # Collect all results
        indexdf = pd.DataFrame([doc['_source'] for doc in all_hits])
        return indexdf
    ##### FIX ME: perhaps we should use the library elasticsearch_dsl instead?
    # see https://elasticsearch-dsl.readthedocs.io/en/latest/
    # and https://stackoverflow.com/questions/53729753/how-to-get-all-results-from-elasticsearch-in-python


def download_selected_file(minio_credential, bucketName, object_name, versionID, downloaddir):
    """
    Downloads a selected file from a Minio bucket.

    Args:
        minio_credential (str): The path to the Minio credential file.
        bucketName (str): The name of the Minio bucket.
        object_name (str): The name of the object to download.
        versionID (str): The version ID of the object to download.
        downloaddir (str): The directory to save the downloaded file.

    Returns:
        bool: True if the file was downloaded successfully, False otherwise.
    """
    with open(minio_credential, 'r') as file:
        keys = json.load(file)

    minio_client = minio.Minio(
        endpoint="localhost:9411",
        access_key=keys["accessKey"],
        secret_key=keys["secretKey"],
        secure=False 
    )
    try:
        os.system("mkdir -p {}".format(downloaddir))
        file_path = os.path.join(downloaddir, object_name)        
        minio_client.fget_object(bucket_name = bucketName, 
                                 object_name = object_name, 
                                 file_path = file_path, 
                                 version_id = versionID)
        print(f"File '{object_name}' downloaded successfully.")
        return True
    except S3Error as e:
        print(f"Error downloading file: {e}")
        return False
    
def search_with_api_key(search_index, search_query, api_key = "SUZzN3FKQUJOeWdud1JqOElhWDY6d3RmR2VzQWtUZzJqZExtR2NHMVotUQ=="):
    """
    Searches the specified Elasticsearch index using the provided search query and API key.

    Parameters:
    - search_index (str): The name of the Elasticsearch index to search.
    - search_query (dict): The search query to be executed.
    - api_key (str, optional): The API key to authenticate the request. Defaults to a sample API key.

    Returns:
    - search_resdf (pandas.DataFrame): The search results as a DataFrame.
    """
    client = Elasticsearch(
    "http://localhost:9200/",
    api_key=api_key)
    response = client.search(index = search_index, body = search_query)
    search_resdf = pd.DataFrame([doc['_source'] for doc in response['hits']['hits']])
    return(search_resdf)
