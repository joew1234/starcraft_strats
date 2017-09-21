#from scpipeline import SCPipeline
import os
import pandas as pd
from sklearn.decomposition import NMF
import time
import matplotlib.pyplot as plt


def get_file_names(dir_path):
    file_list = []
    for filename in os.listdir(dir_path):
        path = dir_path + '/' + filename
        file_list.append(path)
    return file_list

#need to add error checking and skip file on error
def write_units_df_to_file(minutes=10, dir_path='data', outpath='results'):
    file_list = get_file_names(dir_path)
    init_time = time.time()
    for i, filename in enumerate(file_list):
        start_time = time.time()
        print 'processing file {} of {}, file name: {}'.format(i, len(file_list), filename)
        pipe=SCPipeline(filename)
        df = pd.DataFrame(pipe.get_units_dfs(minutes))
        df.to_csv(outpath+'/'+filename[len(dir_path)+1:-4]+'_'+'.csv', mode='w', index=False)
        print 'took {} seconds'.format(time.time()-start_time)
    elapsed_time = time.time() - init_time
    print 'total time elapsed: {} seconds'.format(elapsed_time)
    print 'average time per file: {} seconds'.format(elapsed_time/len(file_list))

def combine_csv(dir_path='results'):
    df_list = []
    for filename in get_file_names(dir_path):
        df = pd.read_csv(filename)
        df_list.append(df)
    return pd.concat(df_list)

def get_race_df(df, race):
    race_df = df[df['race']==race].dropna(axis='columns', how='all').fillna(value=0).drop(['race', 'Won', 'gamelength'], 1)
    return race_df

def get_all_race_dfs(df):
    return get_race_df(df, 'Zerg'), get_race_df(df, 'Protoss'), get_race_df(df, 'Terran')

def get_strat_unit_df(race_df, num_strats):
    col_names = list(race_df)
    model = NMF(n_components=num_strats)
    model.fit(race_df)
    strat_df = model.components_
    return pd.DataFrame(strat_df, columns = col_names), model.reconstruction_err_

# need to give (1,n) row df as unit_df
def units_to_strat(unit_df, strat_df):
    unit_df_copy = unit_df.copy()
    for unit_name in list(strat_df):
        if not unit_name in list(unit_df_copy):
            unit_df_copy[unit_name]=0
    return strat_df.dot(unit_df_copy.transpose())

def plot_reconstruction_error(race_df, strat_range, race_name, plot=True):
    errors = []
    strats = []
    for num_strats in strat_range:
        strat, error = get_strat_unit_df(race_df, num_strats)
        strats.append(strat)
        errors.append(error)
    if plot:
        plt.title(race_name)
        plt.xlabel('Number of strategies')
        plt.ylabel('Reconstruction error of NMF')
        plt.plot(strat_range, errors)
        plt.show()
    return strats, errors
