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
    page_title="Tutorials",
    page_icon="👋",
    layout = "wide"
)
st.markdown(
    """
    # ECD Data dashboard
    
    ## Introduction

    ## Main tutorials

    ### What is in "Release datasets"?
    
    ### How to search/query and download data?
    """
    )
