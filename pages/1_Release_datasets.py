import streamlit as st
import time
import numpy as np

st.set_page_config(page_title="Release datasets", page_icon="📈", layout = "wide")

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
from st_helper_functions import *

import warnings
warnings.filterwarnings("ignore")


minio_credential = "credentials.macstudio.json"
es_credential = "es_credential.json"

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
    "WGS-hg19 dataset, CNA",
    "WGBS-hg19-lowdepth dataset v0.1"
])


#####--------------------------------------------------------------------#####
##### tab1: WGS-hg19 dataset
#####--------------------------------------------------------------------#####
with tab1:
    input_index = "wgsfeature"
    st.title("WGS-hg19 dataset")
    st.markdown(
    """
    For any question, please contact hieunguyen@genesolutions.vn or hieutran@genesolutions.vn.   
    """
    )
    documents = es.scroll_all_data_from_a_profile(input_index)
    df = pd.DataFrame(documents)
    fulldf = df.copy()
    df = df[(df["Pipeline"] == "WGS_hg19") & (df["Project"] == "WGS") & (df["FileExt"] == "csv")]
    all_input_features = df["FeatureName"].unique()
    selected_feature = st.selectbox(
        'Select a feature',
        (all_input_features))
    df = df[df["FeatureName"] == selected_feature]
    df = df.reset_index().drop("index", axis = 1)
    st.dataframe(df)
       
    st.download_button(
        label="Download feature metadata",
        data=convert_df(df),
        file_name="metadata_{}_{}.WGS_hg19.csv".format(input_index, selected_feature),
        mime="text/csv")
    st.download_button(
        label="Download full metadata",
        data=convert_df(fulldf),
        file_name="metadata_{}.WGS_hg19.csv".format(input_index),
        mime="text/csv")
    
    # Add a text box, input the path you want to download your data
    download_path = st.text_input('Path to download the feature (e.g: /home/hieunguyen/Downloads):')
    
    # click this button to download data from minio to your input path above
    if st.button('Download data from MinIO'):
        if download_path == "":
            st.write("Please input the path to download the data")
        else:
            download_path = os.path.join(download_path, "WGS_hg19") 
            os.system("mkdir -p {}".format(download_path))
            
            # Initialize progress bar
            progress_bar = st.progress(0)
            total_files = df.shape[0]
            
            for i in range(total_files):
                bucketName = df.loc[i]["bucket"]
                object_name = df.loc[i]["FileName"]
                versionID = df.loc[i]["versionID"]

                download_selected_file(minio_credential = minio_credential, 
                                    bucketName = bucketName,
                                    object_name = object_name, 
                                    versionID = versionID, 
                                    downloaddir = download_path)
                
                # Update progress bar
                progress_bar.progress((i + 1) / total_files)
                
                # Print success message to Streamlit console
            st.write(f"Dataset WGS_hg19 downloaded successfully.")

#####--------------------------------------------------------------------#####
##### tab2: WGBS hg19 lowdepth dataset v0.1
#####--------------------------------------------------------------------#####