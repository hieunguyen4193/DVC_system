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

#####----------------------------------------------------------------#####
##### preprocessing metadata for MRD and WGS feature dataset.
#####----------------------------------------------------------------#####

# path_to_project_src = "/Users/hieunguyen/src/DVC_system"
path_to_project_src = "/Users/hieunguyen/src/DVC_system"

path_to_save_prep_metadata = os.path.join(path_to_project_src, "examples/dummy_from_real/prep_metadata")
os.system("mkdir -p {}".format(path_to_save_prep_metadata))

feature_description = {
    "CNA": "CNA - copy number aberration feature, from WGBS low depth data",
    "EM": "EM - end motif, 4bp",
    "EM21":  "similary to EM, but 21bp end motif",
    "FLEN": "fragment length distribution of all dna fragments",
    "GWFP_long": "normalized number of long fragments, >= 150bp dna fragments",
    "GWFP_ratio": "ratio of short to long fragment, less than 150 to greater than 150bp dna fragments",
    "GWFP_short": "normalized number of short fragments, < 150bp dna fragments",
    "GWFP_total": "normalized number of total fragments",
    "GWMD": "genome wide methylation density",
    "TMD": "targeted methylation density at 450 regions"   
}

data_name = "WGBS_lowdepth"
sub_data_name = "GW_TM_feature_v0.1"
metadata = pd.read_excel(os.path.join(path_to_project_src, "ECD_metadata/metadata_cfDNA_lowpdepth.xlsx"))

for feature_name in feature_description.keys():
    all_files = [item for item in pathlib.Path("{}/examples/dummy_from_real/{}/{}/{}".format(path_to_project_src, data_name, sub_data_name, feature_name)).glob("*")
                if ".DS" not in item.name]  
    
    if os.path.isfile(os.path.join(path_to_save_prep_metadata, "{}.{}.{}.metadata.csv".format(data_name, sub_data_name, feature_name))) == False:
        maindf = pd.DataFrame(data = [str(item) for item in all_files], columns=["path"])
        maindf["FileName"] = maindf["path"].apply(lambda x: "{}_{}".format(feature_name, x.split("/")[-1]))
        maindf["FeatureName"] = feature_name
        maindf["Labcode"] = maindf["FileName"].apply(lambda x: x.replace(".csv", "").replace("{}_".format(feature_name), ""))
        maindf = maindf[maindf["Labcode"].isin(metadata.SampleID.unique())]
        maindf["SequencingID"] = maindf["Labcode"]
        maindf["Description"] = feature_description[feature_name]
        maindf["FeatureVersion"] = "v0.1"
        maindf["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        maindf["Pipeline"] = "ECD_WGBS_bsalign"
        maindf["Pipeline_params"] = "default"
        maindf["Pipeline_repo"] = "gitlab"
        maindf["Feature_Pipeline"] = "WCD_WGBS_bsalign_GW_TM_feature_v0.1"
        maindf["Feature_Pipeline_params"] = "default"
        maindf["Feature_Pipeline_repo"] = "gitlab"
        maindf["Ref_genome"] = "hg19"
        maindf["Input"] = "bsalign files"
        maindf["Project"] = "ECD_WGBS"
        maindf["Sub_project"] = "lowdepth_data"

        maindf["label1"] = maindf["Labcode"].apply(lambda x: metadata[metadata["SampleID"] == x]["Label"].values[0] if x in metadata["SampleID"].values else "not available")
        maindf["label2"] = maindf["Labcode"].apply(lambda x: metadata[metadata["SampleID"] == x]["Run_TM"].values[0] if x in metadata["SampleID"].values else "not available")
        maindf["label3"] = maindf["Labcode"].apply(lambda x: metadata[metadata["SampleID"] == x]["Run_GW"].values[0] if x in metadata["SampleID"].values else "not available")

        maindf["label4"] = "not available"

        maindf["Note"] = "not available"
        maindf["member"] = "hieunguyen,hieutran"

        maindf.to_csv(os.path.join(path_to_save_prep_metadata, "{}.{}.{}.metadata.csv".format(data_name, sub_data_name, feature_name)), index = False)
    else:
        maindf = pd.read_csv(os.path.join(path_to_save_prep_metadata, "{}.{}.{}.metadata.csv".format(data_name, sub_data_name, feature_name)))
        print("The metadata has been already generated")
    maindf = maindf.set_index("path")
    input_dict = maindf.to_dict(orient = "index") # the input metadata is ready to be added to the database elasticsearch

    ##### Credential
    minio_credential = os.path.join(path_to_project_src, "credentials.macstudio.json")
    es_credential = os.path.join(path_to_project_src, "es_credential.json")

    bamBucket = RDSBucket( 
                            minio_credential = minio_credential, 
                            bucketName = "wgbsfeature-v0.1",
                            PROFILE_NAME = "wgbsfeature",
                            DATA_PROFILES = DATA_PROFILES,
                            es_credential = es_credential, 
                            versioning = True, 
                            verbose = False)
    bamBucket.initBucket()

    for path in tqdm(input_dict.keys()):
        file_metadata = input_dict[path]
        bamBucket.upload_file_to_bucket(path_to_file = path, 
                                        object_name= file_metadata["FileName"], 
                                        file_metadata = file_metadata)