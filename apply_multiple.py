from pipeline import SCPipeline
import os
import pandas as pd


def get_file_names(dir_path='data'):
    file_list = []
    for filename in os.listdir(dir_path):
        path = dir_path + '/' + filename
        file_list.append(path)
    return file_list

def get_strats_df(minutes=10, dir_path='data'):
    file_list = get_file_names(dir_path)
    strats_list = []
    for filename in file_list:
        pipe=SCPipeline(filename)
        strats_list += pipe.get_strategy(minutes)
    strats_df = pd.DataFrame(strats_list)
    return strats_df

def get_race_df(df, race):
    race_df = df[df['race']==race].dropna(axis='columns').drop('race', 1)
    return race_df

# if __name__ == '__main__':
#     strats_df = get_strats_df()
