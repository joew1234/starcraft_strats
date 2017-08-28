from collections import Counter, defaultdict
import torchcraft as tc
from torchcraft import replayer
import pandas as pd


class SCPipeline():
    def __init__(self, replay_file, num_players=2):
        self.replay = replayer.load(replay_file)
        self.gamelength = len(self.replay)
        self.unit_id_dict = tc.Constants.unittypes._dict
        self.num_players = num_players
        self.races = {}
        for pid in range(num_players):
            self.races[pid] = self.get_race(self.get_units(0)[pid].keys()[0])#get the first unit from the first frame

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

    def get_strategy(self, minutes):
        '''
        minutes: int, number of minutes from start of game to collect data on. Note that there are 8 frames per second so 480 frames per minute
        returns (list of pandas series, one for each player)
        '''
        strat = self.units_built(xrange(min(minutes*480, self.gamelength)))
        strat_list = []
        for pid in range(self.num_players):
            series = pd.Series(strat[pid])
            series['race'] = self.races[pid]
            strat_list.append(series)
        return strat_list



if __name__ == '__main__':
    pipe = SCPipeline("data/bwrep_70921.tcr")
