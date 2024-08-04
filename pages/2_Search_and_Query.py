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
from st_helper_functions import *

import warnings
warnings.filterwarnings("ignore")

import streamlit as st 

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
            disabled=["widgets"],
            hide_index=True,
        )
    else:
        st.write("No results found.")
    
    csv = convert_df(search_res)
    st.download_button(
        label="Download metadata",
        data=csv,
        file_name="searh_results.csv",
        mime="text/csv")
    # Add a text box, input the path you want to download your data
    download_path = st.text_input('Path to download the feature (e.g: /home/hieunguyen/Downloads):')
    
    # click this button to download data from minio to your input path above
    if st.button('Download data from MinIO'):
        if download_path == "":
            st.write("Please input the path to download the data")
        else:
            download_path = os.path.join(download_path, "query_dataset_{}".format(datetime.now().strftime("%Y%m%d_%H%M%S"))) 
            os.system("mkdir -p {}".format(download_path))
            
            # Initialize progress bar
            progress_bar = st.progress(0)
            total_files = search_res.shape[0]
            
            for i in range(total_files):
                bucketName = search_res.loc[i]["bucket"]
                object_name = search_res.loc[i]["FileName"]
                versionID = search_res.loc[i]["versionID"]

                download_selected_file(minio_credential = minio_credential, 
                                    bucketName = bucketName,
                                    object_name = object_name, 
                                    versionID = versionID, 
                                    downloaddir = download_path)
                
                # Update progress bar
                progress_bar.progress((i + 1) / total_files)
                
                # Print success message to Streamlit console
            st.write(f"Query dataset downloaded successfully.")
