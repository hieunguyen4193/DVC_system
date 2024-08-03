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

import streamlit as st

st.set_page_config(
    page_title="ECD Data Dashboard",
    page_icon="👋",
)

st.write("# Welcome to ECD data dashboard! 👋")

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

tab1, tab2 = st.tabs([
    "General information", 
    "Data profiles"])

with tab1:
    st.markdown(
    """
    # ECD Data dashboard
    
    ## Introduction

    ## Change log

    ## To-do
    """
    )

with tab2:
    st.header("All ECD datasets")
    selected_index = st.selectbox(
        'All available indices',
        (all_indices))
    documents = es.scroll_all_data_from_a_profile(selected_index)
    df = pd.DataFrame(documents)
    st.dataframe(df, height = 1000)
   