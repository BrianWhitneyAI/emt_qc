from msilib.schema import Directory
import aicspylibczi
from lxml import etree
import os
import os.path
from os.path import exists
import pandas as pd
from datetime import datetime

# This Script looks at a directory with mulitple czi files from a block experiment, and
# finds how long each of the blocks run for. The directory should either have all .czi
# files in the directory or in subdirectories of the chosen directory. It writes a .csv
# and .txt file with all the relevant data to the directory given.
# Outputs a pandas dataframe with all info as well.

# Change directory where EMT czi files are located belows

#PROD_DIR = '/allen/aics/microscopy/PRODUCTION/PIPELINE_8_1'


# Runs emt block duration qc on a single experiment (directory on the isilon). Input is the path to the directory.
def emt_block_duration(block_exp_dir):

    all_data = list()
    # Iterate through all
    for dirpath, dirnames, filenames in os.walk(block_exp_dir):
        for filename in [f for f in filenames if f.endswith('.czi')]:
            img = aicspylibczi.CziFile(os.path.join(dirpath, filename))
            block_num = int(filename[filename.find('Block') + 5 : filename.find('Block') + 6])
            if block_num < 1:
                continue
            z = 0
            c = 0
            t = 0
            s = 0
            sub_metadata = img.read_subblock_metadata(Z=z, C=c, T=t, R=0, S=s, I=0, H=0, V=0)
            metablock = sub_metadata[0][1]
            img_lxml = etree.fromstring(metablock)
            a_time = img_lxml.find('.//AcquisitionTime').text
            date = a_time[:a_time.find('T')]
            start_time = a_time[a_time.find('T')+1 : a_time.find('.')]
            full_datetime = datetime.strptime(f'{date} {start_time}', '%Y-%m-%d %H:%M:%S')
            binning = img.meta.find("./Metadata/Information/Image/Dimensions/Channels/Channel/DetectorSettings/Binning").text
            all_data.append(list([block_num, full_datetime, binning]))

    all_data_df = pd.DataFrame(all_data, columns=['Block', 'Full_datetime', 'Binning']).sort_values('Block')
    all_data_df = all_data_df.reset_index(drop=True)
    durations_each_block = list()
    durations_total = list()
    for i, row in all_data_df.iterrows():
        if i == len(all_data_df)-1:
            durations_each_block.append('N/A')
            durations_total.append('N/A')
        else:
            durations_each_block.append(all_data_df.iloc[i+1]['Full_datetime']- all_data_df.iloc[i]['Full_datetime'])
            durations_total.append(all_data_df.iloc[i+1]['Full_datetime'] - all_data_df.iloc[0]['Full_datetime'])

    all_data_df['Duration_single_Block'] = durations_each_block
    all_data_df['Duration_total'] = durations_total
    # print(f'Experiment file location: {block_exp_dir}')
    with open(f'{block_exp_dir}/block_durations.txt', 'w') as f:
        print(all_data_df, file = f)

    all_data_df.to_csv(f'{block_exp_dir}/block_durations.csv')

    return all_data_df


# Runs all folders in the PROD_DIR with emt_block_duration qc
def emt_block_qc_run_all(dir, reprocess = False):

    for folder in os.listdir(dir):
        if reprocess == True:
            if exists(f'{dir}/{folder}/block_durations.txt') or exists(f'{dir}/block_durations.txt'):
                print(f'Already completed: {folder}')
                continue
        elif reprocess == False:
            emt_block_duration(f'{dir}/{folder}')
            print(f'Completed: {folder}')


def folder_name_fomatter(main_folder):
        
    while [dirname for (_, dirnames,_) in os.walk(main_folder) for dirname in dirnames if dirname.endswith('.czi')]:
        for (dirpath, dirnames, _) in os.walk(main_folder):
            for foldername in [f for f in dirnames if f.endswith('.czi')]:
                folder_no_suffix, _ = os.path.splitext(foldername)
                os.chdir(dirpath)
                os.rename(foldername, folder_no_suffix)       
        os.chdir(main_folder)


def concat_block_dur(dir_master):

    outputname = 'concatenated_block_duraiton.csv'
    if os.path.exists(f'{dir_master}/{outputname}'):
        df = pd.read_csv(f'{dir_master}/{outputname}')
    else:
        df = pd.DataFrame(columns=['Experiment','Block', 'Full_datetime', 'Binning','Duration_single_Block','Duration_total'])
    for (dirpath, _, filenames) in os.walk(dir_master):
        for filename in [f for f in filenames if f.endswith('block_durations.csv')]:
            experiment = os.path.basename(dirpath)
            if not len(df[df['Experiment'] == experiment].index) == 7:
                if not df[df['Experiment'] == experiment].empty:
                    df = df[(df.Experiments == experiment)]
                temp = pd.read_csv(f'{dirpath}/{filename}', index_col=0)
                temp.insert(0,'Experiment', experiment)
                df = df.append(temp, ignore_index = True)
    df.to_csv(f'{dir_master}/{outputname}', index = False)


def concat_max_min_dur(dir_master):

    outputname = 'concatenated_MaxMin_block_duraiton.csv'
    if os.path.exists(f'{dir_master}/{outputname}'):
        df = pd.read_csv(f'{dir_master}/{outputname}')
    else:
        df = pd.DataFrame(columns=['Experiment','Max Block Duration', 'Max Block Number', 'Min Block Duration','Min Block Number'])
    for dirpath, _, filenames in os.walk(dir_master):
        for filename in [f for f in filenames if f.endswith('block_durations.csv')]:
            experiment = os.path.basename(dirpath)
            if df[df['Experiment'] == experiment].empty:
                temp = pd.read_csv(f'{dirpath}/{filename}', index_col=0)
                temp.Duration_single_Block = pd.to_timedelta(temp.Duration_single_Block)
                rowdata = [experiment]
                rowdata.append(temp.Duration_single_Block.max())
                rowdata.append(temp[temp.Duration_single_Block == temp.Duration_single_Block.max()].Block.tolist())
                rowdata.append(temp.Duration_single_Block.min())
                rowdata.append(temp[temp.Duration_single_Block == temp.Duration_single_Block.min()].Block.tolist())
                rowdata = pd.Series(rowdata, index = df.columns)
                df = df.append(rowdata, ignore_index=True)
    df.to_csv(f'{dir_master}/{outputname}', index = False)

def run_all(dir):
    folder_name_fomatter(dir)
    emt_block_qc_run_all(dir)
    # concat_block_dur(dir)
    # concat_max_min_dur