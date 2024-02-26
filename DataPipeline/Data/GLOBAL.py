import json
"""
Here are global variables that contain information like files paths, csv paths, etx...
dont change the value of any of these variables
"""

class Data:
    processor_dir = 'Data/to_process'
    processor_debates_dir = 'Data/to_process/debates'
    processor_bills_dir = 'Data/to_process/bills'

    csv_files_dir = 'Data/csv_files'
    debates_files_dir = 'Data/csv_files/debates_files'

    progress_json = 'Data/progress.json'

    @staticmethod
    def get_progress():
        with open(Data.progress_json, "r") as json_file:
            my_dict = json.load(json_file)

        return my_dict


    @staticmethod
    def update_progress(new_dict):
        with open(Data.progress_json, 'w') as file:
            json.dump(new_dict, file, indent=4)
