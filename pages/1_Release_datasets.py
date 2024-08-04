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
    "WGS-hg19 dataset, CNA",
    "WGBS-hg19-lowdepth dataset v0.1"
])


#####--------------------------------------------------------------------#####
##### tab1: WGS-hg19 dataset
#####--------------------------------------------------------------------#####
with tab1:
    input_index = "wgsfeature"
    st.title("WGS-hg19 dataset")
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
    
    # Add a text box
    download_path = st.text_input('Path to download the feature (e.g: /home/hieunguyen/Downloads):')
    st.write(f'Download path: {download_path}')
    
#####--------------------------------------------------------------------#####
##### tab2: WGBS hg19 lowdepth dataset v0.1
#####--------------------------------------------------------------------#####