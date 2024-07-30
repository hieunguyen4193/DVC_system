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
data_name = "MRD_WGS_hg38"

all_files = [item for item in pathlib.Path("{}/examples/dummy_from_real/{}/Bam_file".format(path_to_project_src, data_name)).glob("*")
                if ".DS" not in item.name]  
metadata_wgs = pd.read_excel("/Users/hieunguyen/src/DVC_system/ECD_metadata/metadata_WGS_20240606.xlsx")[["SampleID", "Label"]]

metadata_wgs["True_label"] = metadata_wgs["Label"]
metadata_wgs.columns = ["SampleID", "Cancer", "True_label"]
metadata_mrd = pd.read_excel("{}/ECD_metadata/metadata_MRD_20240606.xlsx".format(path_to_project_src))[["SampleID", "Cancer", "True_label"]]
metadata_mrd["project"] = "MRD"
metadata_wgs["project"] = "WGS"
metadata = pd.concat([metadata_wgs, metadata_mrd], axis = 0)

##### generate metadata template according to the profile "bamfile"
if os.path.isfile(os.path.join(path_to_save_prep_metadata, "{}.metadata.csv".format(data_name))) == False:
    maindf = pd.DataFrame(data = [str(item) for item in all_files], columns=["path"])
    maindf["FileName"] = maindf["path"].apply(lambda x: os.path.basename(x))
    maindf["FileType"] = "intemediate_file"
    maindf["FileExt"] = maindf["path"].apply(lambda x: os.path.basename(x).split(".")[-1])
    maindf["Labcode"] = maindf["FileName"].apply(lambda x: x.split("_")[0].split("-")[1] if "-" in x else x.split("_")[0])
    maindf["SequencingID"] = maindf["Labcode"]
    maindf["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    maindf["Pipeline"] = maindf["Labcode"].apply(lambda x: 
                                                        "WGS_hg38" if x in metadata[metadata["project"] == "WGS"]["SampleID"].values else "MRD_hg38")
    maindf["Pipeline_params"] = "default"
    maindf["Pipeline_repo"] = "gitlab"
    maindf["Project"] = maindf["Labcode"].apply(lambda x: "WGS" if x in metadata[metadata["project"] == "WGS"]["SampleID"].values else "MRD")
    maindf["Sub_project"] = maindf["Labcode"].apply(lambda x: "WGS_baseline_features" if x in metadata[metadata["project"] == "WGS"]["SampleID"].values else "MRD_baseline_features")
    maindf["Ref_genome"] = "hg38"
    maindf["label1"] = maindf["Labcode"].apply(lambda x: metadata[metadata["SampleID"] == x]["Cancer"].values[0] if x in metadata["SampleID"].values else "not available")
    maindf["label2"] = maindf["Labcode"].apply(lambda x: metadata[metadata["SampleID"] == x]["True_label"].values[0] if x in metadata["SampleID"].values else "not available")
    maindf["label3"] = maindf["Labcode"].apply(lambda x: "non-UMI" if x in metadata[metadata["project"] == "WGS"]["SampleID"].values else "UMI")
    maindf["label4"] = "not available"
    maindf["Note"] = "not available"
    maindf["member"] = "hieunguyen,hieutran"
    maindf.to_csv(os.path.join(path_to_save_prep_metadata, "{}.metadata.csv".format(data_name)), index = False)
else:
    maindf = pd.read_csv(os.path.join(path_to_save_prep_metadata, "{}.metadata.csv".format(data_name)))
    print("The metadata has been already generated")
maindf = maindf.set_index("path")
input_dict = maindf.to_dict(orient = "index") # the input metadata is ready to be added to the database elasticsearch

##### Credential
minio_credential = os.path.join(path_to_project_src, "credentials.macstudio.json")
es_credential = os.path.join(path_to_project_src, "es_credential.json")

bamBucket = RDSBucket( 
                        minio_credential = minio_credential, 
                        bucketName = "bam",
                        PROFILE_NAME = "bamfile",
                        DATA_PROFILES = DATA_PROFILES,
                        es_credential = es_credential, 
                        versioning = True, 
                        verbose = False)
bamBucket.initBucket()

for path in tqdm(input_dict.keys()):
    file_metadata = input_dict[path]
    bamBucket.upload_file_to_bucket(path_to_file = path, 
                                    object_name= file_metadata["FileName"], 
                                    file_metadata = file_metadata, 
                                    update_version = True)