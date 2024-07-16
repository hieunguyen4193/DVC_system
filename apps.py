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

##### Examples
# search_query = {
#   "query": {
#     "match": {
#       "Labcode": "ZLBE113NB"
#     }
#   }
# }

#####----------------------------------------------------------------#####
##### preprocessing metadata for bam file
#####----------------------------------------------------------------#####

path_to_save_prep_metadata = "/Users/hieunguyen/src/DVC_system/examples/dummy_from_real/prep_metadata"
os.system("mkdir -p {}".format(path_to_save_prep_metadata))

path_to_main_input = "./examples/dummy_data"    
minio_credential = "credentials.mb.json"
es_credential = "es_credential.json"

donwloaddir = "./examples/download"
os.system("mkdir  -p {}".format(donwloaddir))

##### genearte the connection to Elasticsearch
es = ESearch(es_credential = es_credential)
all_indices = [item for item in es.es.indices.get_alias(index="*") if "." not in item]
tab1, tab2, tab3 = st.tabs(["Release dataset", "Data summary", "Search query"])

with tab1:
    st.header("Release dataset")

with tab2:
    st.header("All ECD datasets")
    selected_index = st.selectbox(
        'All available indices',
        (all_indices))
   
   # TO DO: list all buckets that use the index
   # Choose th bucket 
   # Then show the descriptive statistics of the bucket/index. 
   
with tab3:
    st.header("Search and Query")
    # Define search index
    search_indices = st.text_input("Enter the index:")

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
        search_res = es.search(search_indices=search_indices, search_query=search_query)
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

   


