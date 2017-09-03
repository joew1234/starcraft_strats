from collections import Counter, defaultdict
import torchcraft as tc
from torchcraft import replayer
import pandas as pd


class SCPipeline():
    def __init__(self, replay_file, num_players=2):
        self.replay = replayer.load(replay_file)
        self.gamelength = len(self.replay)
        self.unit_id_dict = tc.Constants.unittypes._dict
        self.isbuilding = tc.Constants.isbuilding
        self.isworker = tc.Constants.isworker
        self.num_players = num_players
        self.races = {}
        for pid in range(num_players):
            self.races[pid] = self.get_race(self.get_units(0)[pid].keys()[0])#get the first unit from the first frame
        self.winner=self.get_winner()

    def get_race(self, unit_name):
        '''
        unit_name: string or int, can be name or unit id of unit
        returns (string) race of unit
        '''
        race_dict = tc.Constants.staticvalues['getRace']
        return race_dict[unit_name]

    def _units_from_frame(self, frame):
        '''
        frame: torchcraft frame
        returns (dictionary) player_id: Counter of unit types
        '''
        player_unit_count = {}
        for pid in range(self.num_players):
            units = [self.unit_id_dict[unit.type] for unit in frame.units[pid]]
            units_count = Counter(units)
            player_unit_count[pid]=units_count
        return player_unit_count

    def get_units(self, frame_id):
        return self._units_from_frame(self.replay.getFrame(frame_id))

    def print_frames(self, frame_ids):
        '''
        Print unit counts in a human readable format.
        replay: torchcraft replay
        frame_ids(iterable of ints): frame ids to be displayed
        returns None
        '''
        for idx in frame_ids:
            unit_count = self.frame_units(self.replay.getFrame(idx))
            print "player 1 units: ", unit_count[0]
            print "player 2 units: ", unit_count[1]
            print "----------------------------"

    def units_built(self, frame_ids):
        '''
        replay: torchcraft replay
        frame_ids: iterable of frame ids to be processed
        returns (dictionary) pid: Counter of units built
        '''
        units_built = defaultdict(Counter)
        old_units = self.get_units(frame_ids[0]) #initialize prev units to first units
        for idx in frame_ids:
            new_units = self.get_units(idx)
            for pid in range(self.num_players): #pid is player id
                units_built[pid] +=  new_units[pid]-old_units[pid] #note that subtracting counters in this way removes negative values (lost units)
            old_units = new_units
        return units_built

    def get_units_dfs(self, minutes, scale=True):
        '''
        minutes: int, number of minutes from start of game to collect data on. Note that there are 8 frames per second so 480 frames per minute
        scale: bool, replaces counts with % of total units if true
        returns (list of pandas series, one for each player)
        '''
        strat = self.units_built(xrange(min(minutes*480, self.gamelength)))
        units_list = []
        for pid in range(self.num_players):
            series = pd.Series(strat[pid])
            if scale:
                series = self.unit_count_scaler(series)
            series['race'] = self.races[pid]
            series['gamelength'] = self.gamelength #note that the units for this is # of frames
            units_list.append(series)
        return units_list

    def unit_count_scaler(self, series):
        return series/(sum(series))

    def get_building_count(self, frame_id):
        building_count={}
        units_dict = self.get_units(frame_id)
        for pid in range(self.num_players):
            count = 0
            for unit in units_dict[pid]:
                if self.isbuilding(self.unit_id_dict[unit]):
                    count += units_dict[pid][unit]
            building_count[pid] = count
        return building_count
    def get_supply(self, frame_id):
        frame = self.replay.getFrame(frame_id)
        supply = {}
        for pid in range(self.num_players):
            supply[pid] = frame.resources[pid].used_psi
        return supply

    def get_worker_supply(self, frame_id):
        units_dict = self.get_units(frame_id)
        worker_supply = {}
        for pid in range(self.num_players):
            count = 0
            for unit in units_dict[pid]:
                if self.isworker(self.unit_id_dict[unit]):
                    count += units_dict[pid][unit]
            worker_supply[pid] = 2*count
        return worker_supply

    def get_army_supply(self, frame_id):
        total_supply = Counter(self.get_supply(frame_id))
        worker_supply = Counter(self.get_worker_supply(frame_id))
        total_supply.subtract(worker_supply)
        army_supply = dict(total_supply)
        return army_supply

    def get_winner(self):
        building_count = self.get_building_count(self.gamelength-1)
        if building_count[0] <= 1 and building_count[1] >= 2:
            return 1
        if building_count[1] <= 1 and building_count[0] >= 2:
            return 0
        army_supply = self.get_army_supply(self.gamelength-1)
        if army_supply[0] != army_supply[1]:
            return max(army_supply.items(), key=lambda x : x[1])[0]
        if building_count[0] != building_count[1]:
            return max(building_count.items(), key=lambda x : x[1])[0]
        return -1 #-1 means tie



if __name__ == '__main__':
    pipe = SCPipeline("data/bwrep_70921.tcr")
