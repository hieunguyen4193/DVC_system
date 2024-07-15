# Table of contents

- [Introduction](#introduction)
- [Changelogs](#changelogs)
- [Data profiles](#data-profiles)
  - [bam](#bam)

# Introduction

# Changelogs

# Data profiles
See the file "data_profiles.py" for detailed construction of each data profile.

## bam
- `Labcode`: Represents a unique labcode assigned to each sample. The labcode must match the sample information from wet-lab sites.

- `SequencingID`: Each sample can be sequenced multiple times, generating several data with the same `Labcode`. `SequencingID` helps us identify the correct sample and its corresponding sequencing data.

- `FileName`: Represents the object name that is uniquely identified in minio.

- `FileType`: Can be either `feature` or `intermediate file`. `Feature` indicates that the data is ready-to-use as features for further downstream analysis or machine learning/deep learning model construction and evaluation. `Intermediate file` indicates that the file is an important intermediate file of a pipeline (e.g., `.BAM` file). Such files should be kept to avoid re-running the pipeline, which usually takes a significant amount of time.

- `FileExt`: File extension.

- `Date`: Last modified date/time.

- `Pipeline`: Name of the pipeline used to generate the data.

- `Pipeline_params`: Important pipeline parameters, for reproducibility.

- `Pipeline_repo`: Link to gitlab pipeline repository. 

- `Project`: Project name

- `Sub_project`: Sub-project name

- `Ref_genome`: Reference genome

- `Note`: Additional notes on the pipeline/data.

- `label1-4`: Slots for labeling the data (e.g cancer, control, TOO class, ...)

- `bucket`: Minio bucket name.

## feature

