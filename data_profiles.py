DATA_PROFILES = {
    ##########################################################################
    ###### WGBS BAM FILE (BAM file with methylation information)
    ##########################################################################
    "WGBSbam" : {
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
            "bucket": {
                "type": "text"
            }
        }
    },
    ##########################################################################
    ###### COV file from BISMARK METHYLATION EXTRACTOR
    ##########################################################################
    "bismarkCOV": {
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
            "bucket": {
                "type": "text"
            }
        }
    },
    ##########################################################################
    ###### COV file from BISMARK METHYLATION EXTRACTOR
    ##########################################################################
    "WGSbam" : {
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
            "bucket": {
                "type": "text"
            }
        }
    },
    ##########################################################################
    ###### COV file from BISMARK METHYLATION EXTRACTOR
    ##########################################################################
    "FASTQ" : {
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
            "withUMI": {
                "type": "text"
            },
        }
    }
}