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


#Zerg: 4 strats
#drop Zerg_Larva, Zerg_Egg
'''
zerg strats:
Zerg_0: zergling rush
Zerg_Zergling         4.429133
Zerg_Drone            0.220448
Zerg_Overlord         0.103541
Zerg_Spawning_Pool    0.100562
Zerg_Extractor        0.066363

Zerg_1:building defense
Zerg_Drone            3.899045
Zerg_Overlord         0.483391
Zerg_Creep_Colony     0.371484
Zerg_Hatchery         0.289607
Zerg_Sunken_Colony    0.281907

Zerg_2: hydra/lurker
Zerg_Hydralisk     3.438357
Zerg_Drone         1.359918
Zerg_Overlord      0.599837
Zerg_Lurker_Egg    0.217123
Zerg_Lurker        0.176891

Zerg_3: muta/scourge
Zerg_Mutalisk    2.942482
Zerg_Drone       1.556086
Zerg_Scourge     1.288914
Zerg_Overlord    0.801393
Zerg_Spire       0.174916

Counts of each strat:
1    6702
0    6147
2    1079
3     451


'''

#Terran: 5
#drop Protoss_Pylon
'''
terran5:
** drop strat0
Terran_0: Baseline required units
Terran_SCV             6.641340
Terran_Supply_Depot    0.868604
Terran_Refinery        0.258708
Terran_Factory         0.229373
Terran_Barracks        0.174980

Terran_1: Marine/Medic combo
Terran_Marine            5.203093
Terran_SCV               0.787353
Terran_Medic             0.689715
Terran_Missile_Turret    0.627034
Terran_Supply_Depot      0.498479

Terran_2: Vultures
Terran_Vulture_Spider_Mine    3.602275
Terran_Vulture                2.501073
Terran_Supply_Depot           0.365010
Terran_SCV                    0.335490
Terran_Factory                0.306801

Terran_3: siege tanks
Terran_Siege_Tank_Tank_Mode     3.221178
Terran_Siege_Tank_Siege_Mode    2.272890
Terran_Missile_Turret           0.472626
Terran_Supply_Depot             0.424624
Terran_Vulture                  0.397462

Terran_4: Goliaths, heavy air defense
Terran_Goliath           2.212527
Terran_Missile_Turret    0.846004
Terran_Supply_Depot      0.443947
Terran_Factory           0.266035
Terran_SCV               0.235709

strat counts:
1    6080
2    3960
3    1664
4     169

note that this is with strat0 dropped
'''

#Protoss: 6 strats
#drop Terran_SCV
'''
protoss:
** drop strat0
Protoss_0: Baseline required units
Protoss_Probe          7.687033
Protoss_Pylon          0.316135
Protoss_Assimilator    0.246228
Protoss_Gateway        0.234286
Protoss_Nexus          0.191688

Protoss_1: dragoons, observer for highground vision
Protoss_Dragoon        6.380066
Protoss_Pylon          1.608325
Protoss_Gateway        0.711189
Protoss_Observer       0.528759
Protoss_Observatory    0.213965

Protoss_2: zealots
Protoss_Zealot          5.771848
Protoss_Pylon           0.902310
Protoss_Gateway         0.627979
Protoss_Probe           0.142219
Protoss_High_Templar    0.067037

Protoss_3: reaver drop
Protoss_Scarab     2.501355
Protoss_Reaver     0.449405
Protoss_Pylon      0.357078
Protoss_Probe      0.247175
Protoss_Shuttle    0.203175

Protoss_4: Cannon rush or Cannon defense + Corsairs
Protoss_Photon_Cannon    3.692810
Protoss_Corsair          0.851407
Protoss_High_Templar     0.618876
Protoss_Pylon            0.493986
Protoss_Forge            0.427414

Protoss_5: dark templar rush
Protoss_Pylon           3.646785
Protoss_Gateway         1.288134
Protoss_Dark_Templar    1.076619
Protoss_High_Templar    0.570641
Protoss_Corsair         0.529268

strat counts:
1    9182
2    6024
4     511
5     269
3      53

note that this is with strat0 dropped
'''

'''race matchups
Matchup:  Protoss vs Zerg
Winner:  Zerg
Won 52.9045643154% of 5784 games
----------------------
Matchup:  Terran vs Zerg
Winner:  Terran
Won 51.4611087237% of 4654 games
----------------------
Matchup:  Protoss vs Terran
Winner:  Protoss
Won 50.0619578686% of 5649 games
'''

'''
overall win rates per strategy:

race     Strategy     winrate
Protoss  1.0         0.499455
         2.0         0.487384
         3.0         0.679245
         4.0         0.318982
         5.0         0.490706
Terran   1.0         0.475000
         2.0         0.552525
         3.0         0.503606
         4.0         0.497041
Zerg     0.0         0.494550
         1.0         0.513207
         2.0         0.521779
         3.0         0.547672
'''



'''
most unbalanced win rates:

(('Terran_2Terran_4', 'Terran_2'), (1.0, 6)),
 (('Terran_3Terran_4', 'Terran_3'), (0.9090909090909091, 11)),
 (('Protoss_3Terran_2', 'Protoss_3'), (0.875, 8)),
 (('Protoss_5Terran_1', 'Protoss_5'), (0.8709677419354839, 31)),
 (('Protoss_3Zerg_1', 'Protoss_3'), (0.7647058823529411, 17)),
 (('Terran_4Zerg_2', 'Terran_4'), (0.7272727272727273, 11)),
 (('Protoss_4Zerg_0', 'Zerg_0'), (0.7142857142857143, 175)),
 (('Terran_1Terran_2', 'Terran_2'), (0.7102803738317757, 107)),
 (('Zerg_1Zerg_3', 'Zerg_3'), (0.6935483870967742, 62)),
 (('Protoss_4Zerg_2', 'Zerg_2'), (0.6891891891891891, 74)),
 (('Protoss_2Terran_2', 'Terran_2'), (0.6748466257668712, 163)),
 (('Protoss_4Zerg_1', 'Zerg_1'), (0.6637554585152838, 229)),
 (('Protoss_1Terran_1', 'Protoss_1'), (0.6205395996518712, 1149)),
 (('Zerg_0Zerg_3', 'Zerg_3'), (0.6074766355140186, 107)),
 (('Protoss_2Terran_1', 'Protoss_2'), (0.5942857142857143, 175)),
 (('Protoss_1Zerg_1', 'Zerg_1'), (0.5917808219178082, 365)),
 (('Terran_2Zerg_1', 'Terran_2'), (0.5909090909090909, 198)),
 (('Protoss_5Zerg_1', 'Zerg_1'), (0.5897435897435898, 117)),
 (('Protoss_1Protoss_2', 'Protoss_1'), (0.5678496868475992, 479)),
 (('Protoss_1Terran_2', 'Terran_2'), (0.5475398936170213, 3008)),
 (('Terran_1Zerg_0', 'Terran_1'), (0.5319303338171263, 1378))

with strategy descriptions:

Matchup:  Terran: Goliaths, heavy air defense vs Terran: Vultures
Winner:  Terran: Vultures
Won 100.0% of 6 games
----------------------
Matchup:  Terran: Goliaths, heavy air defense vs Terran: siege tanks
Winner:  Terran: siege tanks
Won 90.9090909091% of 11 games
----------------------
Matchup:  Protoss: reaver drop vs Terran: Vultures
Winner:  Protoss: reaver drop
Won 87.5% of 8 games
----------------------
Matchup:  Protoss: dark templar rush vs Terran: Marine/Medic combo
Winner:  Protoss: dark templar rush
Won 87.0967741935% of 31 games
----------------------
Matchup:  Protoss: reaver drop vs Zerg: building defense
Winner:  Protoss: reaver drop
Won 76.4705882353% of 17 games
----------------------
Matchup:  Terran: Goliaths, heavy air defense vs Zerg: hydra/lurker
Winner:  Terran: Goliaths, heavy air defense
Won 72.7272727273% of 11 games
----------------------
Matchup:  Protoss: Cannon rush or Cannon defense + Corsairs vs Zerg: zergling rush
Winner:  Zerg: zergling rush
Won 71.4285714286% of 175 games
----------------------
Matchup:  Terran: Marine/Medic combo vs Terran: Vultures
Winner:  Terran: Vultures
Won 71.0280373832% of 107 games
----------------------
Matchup:  Zerg: building defense vs Zerg: muta/scourge
Winner:  Zerg: muta/scourge
Won 69.3548387097% of 62 games
----------------------
Matchup:  Protoss: Cannon rush or Cannon defense + Corsairs vs Zerg: hydra/lurker
Winner:  Zerg: hydra/lurker
Won 68.9189189189% of 74 games
----------------------
Matchup:  Protoss: zealot rush vs Terran: Vultures
Winner:  Terran: Vultures
Won 67.4846625767% of 163 games
----------------------
Matchup:  Protoss: Cannon rush or Cannon defense + Corsairs vs Zerg: building defense
Winner:  Zerg: building defense
Won 66.3755458515% of 229 games
----------------------
Matchup:  Protoss: dragoons, observer for highground vision vs Terran: Marine/Medic combo
Winner:  Protoss: dragoons, observer for highground vision
Won 62.0539599652% of 1149 games
----------------------
Matchup:  Zerg: muta/scourge vs Zerg: zergling rush
Winner:  Zerg: muta/scourge
Won 60.7476635514% of 107 games
----------------------
Matchup:  Protoss: zealot rush vs Terran: Marine/Medic combo
Winner:  Protoss: zealot rush
Won 59.4285714286% of 175 games
----------------------
Matchup:  Protoss: dragoons, observer for highground vision vs Zerg: building defense
Winner:  Zerg: building defense
Won 59.1780821918% of 365 games
----------------------
Matchup:  Terran: Vultures vs Zerg: building defense
Winner:  Terran: Vultures
Won 59.0909090909% of 198 games
----------------------
Matchup:  Protoss: dark templar rush vs Zerg: building defense
Winner:  Zerg: building defense
Won 58.9743589744% of 117 games
----------------------
Matchup:  Protoss: dragoons, observer for highground vision vs Protoss: zealot rush
Winner:  Protoss: dragoons, observer for highground vision
Won 56.7849686848% of 479 games
----------------------
Matchup:  Protoss: dragoons, observer for highground vision vs Terran: Vultures
Winner:  Terran: Vultures
Won 54.7539893617% of 3008 games
----------------------
Matchup:  Terran: Marine/Medic combo vs Zerg: zergling rush
Winner:  Terran: Marine/Medic combo
Won 53.1930333817% of 1378 games

'''


''' how often are strats paired together

race     Strategy Pairs
Protoss  12                6991
         13                1114
         14                 714
         15                2071
         23                1865
         24                1461
         25                1626
         34                  46
         35                  10
         45                 140
Terran   12                5369
         13                1095
         14                 556
         15                1217
         23                1667
         24                 982
         25                 865
         34                  46
         35                   2
         45                  74
Zerg     12                6672
         13                 977
         14                 743
         15                1281
         23                2044
         24                1439
         25                1076
         34                  30
         35                   4
         45                 112

'''


'''Gamelength statistics (in minutes)
race     Strategy
Protoss  1.0         17.202981
         2.0         16.055370
         3.0         13.452830
         4.0         13.500693
         5.0         14.154523
Terran   1.0         15.894536
         2.0         19.367717
         3.0         21.297581
         4.0         17.904709
Zerg     0.0         11.590912
         1.0         17.820937
         2.0         14.818360
         3.0         12.944106
'''






if __name__ == '__main__':
    strat_dict = {'Zerg_0': 'Zerg: zergling rush', 'Zerg_1':'Zerg: building defense', 'Zerg_2': 'Zerg: hydra/lurker', 'Zerg_3': 'Zerg: muta/scourge', 'Terran_1': 'Terran: Marine/Medic combo', 'Terran_2': 'Terran: Vultures', 'Terran_3': 'Terran: siege tanks', 'Terran_4': 'Terran: Goliaths, heavy air defense', 'Protoss_1': 'Protoss: dragoons, observer for highground vision', 'Protoss_2': 'Protoss: zealot rush', 'Protoss_3': 'Protoss: reaver drop', 'Protoss_4': 'Protoss: Cannon rush or Cannon defense + Corsairs', 'Protoss_5': 'Protoss: dark templar rush'}
