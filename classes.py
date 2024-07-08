##### connect to the elasticsearch server
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


from DataProfile_JSON_db import *
from minio_utils import *

load_dotenv()

#####-------------------------------------------------------------------#####
# Define elasticsearch object
#####-------------------------------------------------------------------#####
class ESearch:
    def __init__(self, username, password, verbose = False):
        self.username = username
        self.password = password
        self.es = Elasticsearch(
            "http://localhost:9200", # deployed locally, no cloud
            basic_auth=(username, password)) 
        client_info = self.es.info()
        tmp = self.es.cat.indices(index='*', h='index', s='index:asc', format='json')
        self.all_indices = [index['index'] for index in tmp if index['index'][0] != "."] # not show hidden indices
        if verbose:
            print('Connected to Elasticsearch!')
            pprint(client_info.body)
        
    def create_index(self, index_name, metadata_profile):
        self.es.indices.create(index = index_name,  mappings = metadata_profile)

    def insert_document(self, document, index):
        return self.es.index(index = index, body=document)
    
#####-------------------------------------------------------------------#####
# minio credentials, local server.
#####-------------------------------------------------------------------#####
# minio_credentials = "credentials.mb.json"
minio_credentials = "credentials.macstudio.json"


#####-------------------------------------------------------------------#####
# Define a class that includes both ELASTIC SEARCH and MINIO
#####-------------------------------------------------------------------#####

