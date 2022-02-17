import os 
from pathlib import Path

def get_QC_daily_path(
    reference_directory: str, # use path to Argo_QC_daily
    system: str, # Options are ZSD0, ZSD1, ZSD2, ZSD3, 3i0, 3i1
    objective: int,
    date: int
)-> Path:
    opt_cont_files = []
    for opt_dir in os.listdir(f'{reference_directory}/{system}'):
        folder_metadata = opt_dir.split("_")
        folder_metadata = [x.upper() for x in folder_metadata]
        if all(x in folder_metadata for x in [system, f'{objective}X', str(date)]) is True:
            opt_conts = [f for f in os.listdir(f'{reference_directory}/{system}/{opt_dir}') if f.endswith('.czi')]
            for opt_cont in opt_conts:
                opt_cont_files.append(Path(f'{reference_directory}/{system}/{opt_dir}/{opt_cont}'))
    
    if len(opt_cont_files) == 1:
        return Path(opt_cont_files[0])
    elif len(opt_cont_files) == 0:
        raise Exception(f"No files found with system: {system}, objective: {objective}, date: {date}")
    else:
        print(f"Multiple files found with system: {system}, objective: {objective}, date: {date}. Printing all paths, and outputting the first found")
        for i in opt_cont_files:
            print(i)
        return Path(opt_cont_files[0])