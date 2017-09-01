from scpipeline import SCPipeline
import os
import pandas as pd
from sklearn.decomposition import NMF


def get_file_names(dir_path='data'):
    file_list = []
    for filename in os.listdir(dir_path):
        path = dir_path + '/' + filename
        file_list.append(path)
    return file_list

def get_all_units_df(minutes=10, dir_path='data'):
    file_list = get_file_names(dir_path)
    strats_list = []
    for i, filename in enumerate(file_list):
        print 'processing file {} of {}'.format(i, len(file_list))
        pipe=SCPipeline(filename)
        strats_list += pipe.get_units_dfs(minutes)
    strats_df = pd.DataFrame(strats_list)
    return strats_df

def get_race_df(df, race):
    race_df = df[df['race']==race].dropna(axis='columns', how='all').fillna(value=0).drop('race', 1)
    return race_df

def get_all_race_dfs(df):
    return get_race_df(df, 'Zerg'), get_race_df(df, 'Protoss'), get_race_df(df, 'Terran')

def get_strat_unit_df(race_df, num_strats):
    col_names = list(race_df)
    model = NMF(n_components=num_strats)
    model.fit(zerg_df)
    strat_df = model.components_
    return pd.DataFrame(strat_df, columns = col_names)


# need to give (1,n) row df as unit_df
def units_to_strat(unit_df, strat_df):
    unit_df_copy = unit_df.copy()
    for unit_name in list(strat_df):
        if not unit_name in list(unit_df_copy):
            unit_df_copy[unit_name]=0
    return strat_df.dot(unit_df_copy.transpose())




if __name__ == '__main__':
    model = NMF(n_components=2)
    strats_df = get_all_units_df()
    zerg_df, protoss_df, terran_df = get_all_race_dfs(strats_df)
    #W = model.fit_transform(zerg_df)
    #H = model.components_
