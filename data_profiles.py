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
            "label1": {
                "type": "text"
            }, 
            "label2": {
                "type": "text"
            }, 
            "label3": {
                "type": "text"
            }, 
            "label4": {
                "type": "text"
            }, 
            "Note": {
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
            "label1": {
                "type": "text"
            },
            "label2": {
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
    "wgsfeature" : {
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
            "featureVersion": {
                "type": "text"
            },
            "featureName": {
                "type": "text"
            },
            "bioinfo_pipeline": {
                "type": "text"
            },
            "bioinfo_pipeline_params": {
                "type": "text"
            },
            "feature_pipeline": {
                "type": "text"
            },
            "feature_pipeline_params": {
                "type": "text"
            },
            "project": {
                "type": "text"
            }, 
            "sub_project": {
                "type": "text"
            },
            "label1": {
                "type": "text"
            },
            "label2": {
                "type": "text"
            },
            "label3": {
                "type": "text"
            },            
            "Note": {
                "type": "text"
            },
            "bucket": {
                "type": "text"
            }
        }
    },
    ##########################################################################
    ###### tabular feature file, single column, 1 column = 1 sample, rows = features
    ##########################################################################
    "wgbsfeature" : {
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
            "featureVersion": {
                "type": "text"
            },
            "bioinfo_pipeline": {
                "type": "text"
            },
            "bioinfo_pipeline_params": {
                "type": "text"
            },
            "feature_pipeline": {
                "type": "text"
            },
            "methylaionCaller": {
                "type": "text"
            },
            "feature_pipeline_params": {
                "type": "text"
            },
            "project": {
                "type": "text"
            }, 
            "sub_project": {
                "type": "text"
            },
            "label1": {
                "type": "text"
            },
            "label2": {
                "type": "text"
            },
            "label3": {
                "type": "text"
            },            
            "Note": {
                "type": "text"
            },
            "bucket": {
                "type": "text"
            }
        }
    }
}