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
data_name = "WGBS_lowdepth"
sub_data_name = "TM_BAM"

all_files = [item for item in pathlib.Path("{}/examples/dummy_from_real/{}/{}".format(path_to_project_src, data_name, sub_data_name)).glob("*")
                if ".DS" not in item.name]  
metadata = pd.read_excel("./ECD_metadata/metadata_cfDNA_lowpdepth.xlsx")
metadata["FileName"] = metadata["TM_BAM"].apply(lambda x: os.path.basename(str(x)))

#### generate metadata template according to the profile "bamfile"
if os.path.isfile(os.path.join(path_to_save_prep_metadata, "{}.{}.metadata.csv".format(data_name, sub_data_name))) == False:
    maindf = pd.DataFrame(data = [str(item) for item in all_files], columns=["path"])
    maindf["FileName"] = maindf["path"].apply(lambda x: os.path.basename(x))
    maindf["FileType"] = "intemediate_file"
    maindf["FileExt"] = maindf["path"].apply(lambda x: os.path.basename(x).split(".")[-1])
    maindf["Labcode"] = maindf["FileName"].apply(lambda x: metadata[metadata["FileName"] == x]["SampleID"].values[0])
    maindf["SequencingID"] = maindf["Labcode"]
    maindf["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    maindf["Pipeline"] = "ECD_WGBS_TM_hg19"
    maindf["Pipeline_params"] = "default"
    maindf["Pipeline_repo"] = "gitlab"
    maindf["Project"] = "ECD_WGBS"
    maindf["Sub_project"] = "targeted_450_regions"
    maindf["Ref_genome"] = "hg19"

    maindf["label1"] = maindf["Labcode"].apply(lambda x: metadata[metadata["SampleID"] == x]["Label"].values[0] if x in metadata["SampleID"].values else "not available")
    maindf["label2"] = maindf["Labcode"].apply(lambda x: metadata[metadata["SampleID"] == x]["Run_TM"].values[0] if x in metadata["SampleID"].values else "not available")
    maindf["label3"] = maindf["Labcode"].apply(lambda x: metadata[metadata["SampleID"] == x]["Run_GW"].values[0] if x in metadata["SampleID"].values else "not available")

    maindf["label4"] = "not available"

    maindf["Note"] = "not available"
    maindf["member"] = "hieunguyen,hieutran"
    maindf.to_csv(os.path.join(path_to_save_prep_metadata, "{}.{}.metadata.csv".format(data_name, sub_data_name)), index = False)
else:
    maindf = pd.read_csv(os.path.join(path_to_save_prep_metadata, "{}.{}.metadata.csv".format(data_name, sub_data_name)))
    print("The metadata has been already generated")
maindf = maindf.set_index("path")
input_dict = maindf.to_dict(orient = "index") # the input metadata is ready to be added to the database elasticsearch

##### Credential
minio_credential = os.path.join(path_to_project_src, "credentials.macstudio.json")
es_credential = os.path.join(path_to_project_src, "es_credential.json")

bamBucket = RDSBucket( 
                        minio_credential = minio_credential, 
                        bucketName = "lowdepth-tm-bismark-bam",
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
                                    update_version=True)