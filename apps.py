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

st.set_page_config(layout="wide")

#####-------------------------------------------------------------------------------#####
##### Examples: search query with DSL from easlasticsearch
#####-------------------------------------------------------------------------------#####
# search_query = {
#   "query": {
#     "match": {
#       "Labcode": "ZLBE113NB"
#     }
#   }
# }

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

##### define tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Release dataset", 
    "Data profiles",
    "Data buckets", 
    "Search query"])

#####-------------------------------------------------------------------------------#####
##### tab1
##### This tab contains all OFFICIAL release ECD datasets. Members of the ECD project
##### can easily download the datasets by clicking on the download button. Versioning is 
##### supported by the system.
#####-------------------------------------------------------------------------------#####
with tab1:
    st.header("Release dataset")
    subtab1, subtab2 = st.tabs([
    "WGS-hg19 dataset",
    "WGBS-hg19-CNA dataset"
    ])
with subtab1:
    input_index = "wgsfeature"
    st.title("WGS-hg19 dataset")
    documents = es.scroll_all_data_from_a_profile(input_index)
    df = pd.DataFrame(documents)
    df = df[(df["Pipeline"] == "WGS_hg19") & (df["Project"] == "WGS")]
    st.dataframe(df, height = 1000)
    
#####-------------------------------------------------------------------------------#####
##### tab2
#####-------------------------------------------------------------------------------#####
with tab2:
    st.header("All ECD datasets")
    selected_index = st.selectbox(
        'All available indices',
        (all_indices))
    documents = es.scroll_all_data_from_a_profile(selected_index)
    df = pd.DataFrame(documents)
    st.dataframe(df, height = 1000)
    
#####-------------------------------------------------------------------------------#####
##### tab3
#####-------------------------------------------------------------------------------#####
with tab3:
    st.header("Data buckets")
    selected_bucket = st.selectbox(
        'Select a data bucket',
        (all_buckets))
    with open(minio_credential, 'r') as file:
        keys = json.load(file)
        
    minio_client = minio.Minio(
            endpoint="localhost:9411",
            access_key=keys["accessKey"],
            secret_key=keys["secretKey"],
            secure=False)
    
#####-------------------------------------------------------------------------------#####
##### tab4
#####-------------------------------------------------------------------------------#####
with tab4:
    st.header("Search and Query")
    # Define search index
    search_indices = st.selectbox(
        'Select an index',
        (all_indices))

    # Define search query as JSON input
    search_query_json = st.text_area("Enter the search query in JSON format:")

    # Parse the JSON input
    try:
        search_query = json.loads(search_query_json)
    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please correct the input.")
        search_query = None

    # Get the search results if the query is valid
    if search_query:
        search_res = es.search_scroll(search_indices=search_indices, search_query=search_query)
        true_false_df = pd.DataFrame(data = [False for item in range(search_res.shape[0])], columns = ["select"])
        search_res = pd.concat([search_res, true_false_df], axis = 1)
        
        if search_res.shape[0] != 0:
            st.title("Search Results")
            st.data_editor(
                search_res,
                column_config={
                    "selct": st.column_config.CheckboxColumn(
                        "Your favorite?",
                        help="Select your **favorite** widgets",
                        default=False,
                    )
                },
                disabled=["widgets"],
                hide_index=True,
            )

        else:
            st.write("No results found.")
