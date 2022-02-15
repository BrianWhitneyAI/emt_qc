
import os 

def get_QC_daily_path(
    refrence_directory: os.path, # use path to Argo_QC_daily
    system: str,
    search_criteria: list
)-> os.path:
    for (dirpath, dirnames, _) in os.walk(f'{refrence_directory}/{system}'):
        for foldername in dirnames:
            folder_metadata = foldername.split("_")
            if all(item in folder_metadata for item in search_criteria) is True:
                return f'{dirpath}/{foldername}/{foldername}.czi'
    raise Exception("No file found with given critria: " + search_criteria)


