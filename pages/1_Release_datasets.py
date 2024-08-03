import streamlit as st
import time
import numpy as np

st.set_page_config(page_title="Release datasets", page_icon="📈")

st.markdown("# Release datasets")
st.sidebar.header("Release datasets")
st.write(
    """This page contains pre-selected dataset for some ongoing ECD projects"""
)

##### MAIN SCRIPTS
import pandas as pd
import os 
import pathlib 
import glob
from datetime import datetime
from tqdm import tqdm

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

import minio
from minio.error import S3Error
from minio.commonconfig import ENABLED
from minio.versioningconfig import VersioningConfig

from RDSBucket_class import *
from data_profiles import *

import warnings
warnings.filterwarnings("ignore")

minio_credential = "credentials.macstudio.json"
es_credential = "es_credential.json"

donwloaddir = "./examples/download"
os.system("mkdir  -p {}".format(donwloaddir))

##### generate the connection to minio
with open(minio_credential, 'r') as file:
            keys = json.load(file)
        
minio_client = minio.Minio(
            endpoint="localhost:9411",
            access_key=keys["accessKey"],
            secret_key=keys["secretKey"],
            secure=False 
        )
all_buckets = [bucket.name for bucket in minio_client.list_buckets()]

##### generate the connection to Elasticsearch
es = ESearch(es_credential = es_credential)
all_indices = [item for item in es.es.indices.get_alias(index="*") if "." not in item]

