import json
import os

class DataProfileDB:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_database()
        self.record_names = [list(item.keys())[0] for item in self.data]

    def load_database(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as db_file:
                json.dump([], db_file)
        with open(self.filename, 'r') as db_file:
            return json.load(db_file)

    def save_database(self):
        with open(self.filename, 'w') as db_file:
            json.dump(self.data, db_file, indent=4)

    def create_record(self, record, record_name, overwrite = False):
        if record_name in self.record_names:
            if overwrite == False:
                raise ValueError(f"Record with name '{record_name}' already exists.")
            else:
                self.delete_record(record_name)
                self.data.append({record_name: record})
                self.save_database()
        else:
            self.data.append({record_name: record})
            self.save_database()
    def get_record(self, record_name):
        return self.data[self.record_names.index(record_name)]
    def delete_record(self, record_name):
        # find index of the record
        id_to_delete = [list(item.keys())[0] for item in db.data].index(record_name)
        del self.data[id_to_delete]
        self.save_database()

# Example usage
db = DataProfileDB("ALL_DATA_PROFILES.json")

data_profile1 = {
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
        }
    }
}

data_profile2 = {
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
        }
    }
}

db.create_record(
    record = data_profile1, 
    record_name = "dev1",
    overwrite = True)

db.create_record(
    record = data_profile2, 
    record_name = "dev2",
    overwrite = True)
    
