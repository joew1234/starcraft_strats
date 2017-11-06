import pandas as pd
from collections import defaultdict, Counter
from statsmodels.stats.proportion import proportions_ztest
from numpy import argsort

def print_units(strat, num_units=5):
    for row in strat.iterrows():
        print row[1].nlargest(n=num_units)


def game_strats(unit_df, strat_df):
    return strat_df.dot(unit_df.T)

def game_strat_counts(unit_df, strat_df):
    game_strats_df = game_strats(unit_df, strat_df)
    return game_strats_df.idxmax().value_counts()

def top_n_strats(unit_df, strat_df, n):
    game_strats_df = game_strats(unit_df, strat_df)
    top_strats_df = argsort(game_strats_df, axis=0).iloc[-n:,:]
    return top_strats_df

def strat_pairs_column(unit_df, strat_df):
    top_strats_df = top_n_strats(unit_df, strat_df, 2)
    top_strats_df = top_strats_df.applymap(lambda x: x+1)
    top_strats_df = top_strats_df.applymap(str)
    top_strats_df = top_strats_df.iloc[0]+top_strats_df.iloc[1]
    top_strats_df = top_strats_df.apply(lambda x: ''.join(sorted(x)))
    return top_strats_df

def strat_column(unit_df, strat_df):
    game_strats_df = game_strats(unit_df, strat_df)
    return game_strats_df.idxmax()

def get_all_strats_pairs_column(zerg, protoss, terran, zerg_strat, protoss_strat, terran_strat):
    z = strat_pairs_column(zerg, zerg_strat)
    p = strat_pairs_column(protoss, protoss_strat)
    t = strat_pairs_column(terran, terran_strat)
    col = pd.concat([z,p,t])
    col.sort_index(inplace=True)
    return col

def add_strat_pair_column(df, zerg, protoss, terran, zerg_strat, protoss_strat, terran_strat):
    col = get_all_strats_pairs_column(zerg, protoss, terran, zerg_strat, protoss_strat, terran_strat)
    df['Strategy Pairs'] = col
    return df


def clean_zerg(zerg_df):
    zerg_df.drop(['Zerg_Larva', 'Zerg_Egg'],axis=1, inplace=True)

def clean_protoss(protoss_df):
    protoss_df.drop('Terran_SCV', axis=1, inplace=True)

def clean_terran(terran_df):
    terran_df.drop('Protoss_Pylon', axis=1, inplace=True)

def get_all_strats_column(zerg, protoss, terran, zerg_strat, protoss_strat, terran_strat):
    z = strat_column(zerg, zerg_strat)
    p = strat_column(protoss, protoss_strat)
    t = strat_column(terran, terran_strat)
    col = pd.concat([z,p,t])
    col.sort_index(inplace=True)
    return col

def add_strat_col(df, zerg, protoss, terran, zerg_strat, protoss_strat, terran_strat):
    col = get_all_strats_column(zerg, protoss, terran, zerg_strat, protoss_strat, terran_strat)
    df['Strategy'] = col
    return df

def get_race_mu(df):
    num_games = (df.shape[0]+1)/2
    results = []
    matchup_totals = defaultdict(int)
    for game_num in xrange(num_games):
        player1 = df.loc[2*game_num]
        player2 = df.loc[2*game_num+1]
        p1race = player1['race']
        p2race = player2['race']
        if p1race != p2race: #remove mirror matches
            matchup = ' vs '.join(sorted([p1race, p2race]))
            matchup_totals[matchup]+=1
            if player1['Won']:
                result = (matchup, p1race)
            else:
                result = (matchup, p2race)
            results.append(result)
    return results, matchup_totals

def mu_win_percent(df):
    results, matchup_totals = get_race_mu(df)
    results_count = Counter(results)
    result =  {(matchup, winner):((float(count)/matchup_totals[matchup]), matchup_totals[matchup]) for (matchup, winner), count in results_count.iteritems()}
    result_list = list(result.items())
    result_sorted = sorted(result_list, key= lambda x: x[1][0], reverse=True)
    return result_sorted

def get_race_strat_mu(df):
    num_games = (df.shape[0]+1)/2
    results = []
    matchup_totals = defaultdict(int)
    for game_num in xrange(num_games):
        player1 = df.loc[2*game_num]
        player2 = df.loc[2*game_num+1]
        p1strat = strat_dict[player1['race']+'_'+str(int(player1['Strategy']))]
        p2strat = strat_dict[player2['race']+'_'+str(int(player2['Strategy']))]
        if p1strat != p2strat: #remove mirror matches
            matchup = ' vs '.join(sorted([p1strat, p2strat]))
            matchup_totals[matchup]+=1
            if player1['Won']:
                result = (matchup, p1strat)
            else:
                result = (matchup, p2strat)
            results.append(result)
    return results, matchup_totals

def mu_strategy_win_percent(df):
    results, matchup_totals = get_race_strat_mu(df)
    results_count = Counter(results)
    result =  {(matchup, winner):((float(count)/matchup_totals[matchup]), matchup_totals[matchup]) for (matchup, winner), count in results_count.iteritems()}
    result_list = list(result.items())
    result_sorted = sorted(result_list, key= lambda x: x[1][0], reverse=True)
    return result_sorted

    '''if ztest_prob((float(count)/matchup_totals[matchup]), matchup_totals[matchup])>.95 and matchup_totals[matchup]>5'''

def ztest_prob(win_percent, matchup_total):
    return proportions_ztest(win_percent*matchup_total, matchup_total, value=.5, alternative='smaller')[1]

def print_strategy_matchup_results(df):
    results = mu_strategy_win_percent(df)
    for result in results:
        print "Matchup: ", result[0][0]
        print "Winner: ", result[0][1]
        print "Won {}% of {} games".format(100*result[1][0], result[1][1])
        print "----------------------"

def print_race_matchup_results(df):
    results = mu_win_percent(df)
    for result in results:
        print "Matchup: ", result[0][0]
        print "Winner: ", result[0][1]
        print "Won {}% of {} games".format(100*result[1][0], result[1][1])
        print "----------------------"

def get_strat_pair_counts(df):
    return df.groupby(['race', 'Strategy Pairs']).size()

def gamelength_per_strat(df):
    return df.groupby(['race', 'Strategy'])['gamelength'].mean().divide(480)


if __name__ == '__main__':
    strat_dict = {'Zerg_0': 'Zerg: zergling rush', 'Zerg_1':'Zerg: building defense', 'Zerg_2': 'Zerg: hydra/lurker', 'Zerg_3': 'Zerg: muta/scourge', 'Terran_1': 'Terran: Marine/Medic combo', 'Terran_2': 'Terran: Vultures', 'Terran_3': 'Terran: siege tanks', 'Terran_4': 'Terran: Goliaths, heavy air defense', 'Protoss_1': 'Protoss: dragoons, observer for highground vision', 'Protoss_2': 'Protoss: zealot rush', 'Protoss_3': 'Protoss: reaver drop', 'Protoss_4': 'Protoss: Cannon rush or Cannon defense + Corsairs', 'Protoss_5': 'Protoss: dark templar rush'}
