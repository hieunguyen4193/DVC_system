DATA_PROFILES = {
    ##########################################################################
    ###### WGBS BAM FILE (BAM file with methylation information)
    ##########################################################################
    "wgbsbam" : {
        "properties": {
            "Labcode": {
                "type": "text"
            },
            "SequencingID": {
                "type": "text"
            },
            "FileName": {
                "type": "text"
            },
            "FileType": {
                "type": "text"
            },
            "Date": {
                "type": "date"
            },
            "pipeline": {
                "type": "text"
            },
            "methylationCaller": {
                "type": "text"
            },
            "project": {
                "type": "text"
            },
            "sub_project": {
                "type": "text"
            },
            "ref_genome": {
                "type": "text"
            },
            "depth": {
                "type": "text"
            },
            "cancer_label": {
                "type": "text"
            }, 
            "bucket": {
                "type": "text"
            }
        }
    },
    ##########################################################################
    ###### COV file from BISMARK METHYLATION EXTRACTOR
    ##########################################################################
    "bismarkcov": {
        "properties": {
            "Labcode": {
                "type": "text"
            },
            "SequencingID": {
                "type": "text"
            },
            "FileName": {
                "type": "text"
            },
            "FileType": {
                "type": "text"
            },
            "Date": {
                "type": "date"
            },
            "pipeline": {
                "type": "text"
            },
            "project": {
                "type": "text"
            },
            "sub_project": {
                "type": "text"
            },
            "ref_genome": {
                "type": "text"
            },
            "methylationCaller": {
                "type": "text"
            },
            "filterDepth": {
                "type": "text"
            },
            "cancer_label": {
                "type": "text"
            }, 
            "bucket": {
                "type": "text"
            }
        }
    },
    ##########################################################################
    ###### COV file from BISMARK METHYLATION EXTRACTOR
    ##########################################################################
    "wgsbam" : {
        "properties": {
            "Labcode": {
                "type": "text"
            },
            "SequencingID": {
                "type": "text"
            },
            "FileName": {
                "type": "text"
            },
            "FileType": {
                "type": "text"
            },
            "Date": {
                "type": "date"
            },
            "pipeline": {
                "type": "text"
            },
            "project": {
                "type": "text"
            },
            "sub_project": {
                "type": "text"
            },
            "ref_genome": {
                "type": "text"
            },
            "depth": {
                "type": "text"
            },
            "cancer_label": {
                "type": "text"
            }, 
            "bucket": {
                "type": "text"
            }
        }
    },
    ##########################################################################
    ###### COV file from BISMARK METHYLATION EXTRACTOR
    ##########################################################################
    "fastq" : {
        "properties": {
            "Labcode": {
                "type": "text"
            },
            "SequencingID": {
                "type": "text"
            }, 
            "FileName": {
                "type": "text"
            },
            "FileType": {
                "type": "text"
            },
            "Date": {
                "type": "date"
            },
            "readlen": {
                "type": "integer"
            },
            "cancer_label": {
                "type": "text"
            }, 
            "withUMI": {
                "type": "text"
            }
        }
    },
    ##########################################################################
    ###### tabular feature file, single column, 1 column = 1 sample, rows = features
    ##########################################################################
    "csvfeature" : {
        "properties": {
            "Labcode": {
                "type": "text"
            },
            "SequencingID": {
                "type": "text"
            }, 
            "FileName": {
                "type": "text"
            },
            "FileType": {
                "type": "text"
            },
            "Date": {
                "type": "date"
            },
            "featureName": {
                "type": "text"
            },
            "project": {
                "type": "text"
            },
            "cancer_label": {
                "type": "text"
            }, 
            "sub_project": {
                "type": "text"
            }
        }
    },
    ##########################################################################
    ###### .rds Robject feature file, single sample
    ##########################################################################
    "rdsfeature" : {
        "properties": {
            "Labcode": {
                "type": "text"
            },
            "SequencingID": {
                "type": "text"
            }, 
            "FileName": {
                "type": "text"
            },
            "FileType": {
                "type": "text"
            },
            "Date": {
                "type": "date"
            },
            "featureName": {
                "type": "text"
            },
            "project": {
                "type": "text"
            },
            "cancer_label": {
                "type": "text"
            }, 
            "sub_project": {
                "type": "text"
            }
        }
    }
}