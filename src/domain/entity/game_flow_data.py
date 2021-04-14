import pandas as pd


class GameFlowData:
    def __init__(self):
        self._data = []

    def append(self, data):
        self._data.append(data)

    def format(self):
        cols = ['frame_num', 'object_type', 'is_valid', 'player_num',
                'chain_num', 'is_main_chain', 'eliminated_num',
                'eliminated_percentage', 'nuisance', 'nuisance_count',
                'is_start']
        df = pd.DataFrame(index=[], columns=cols)
        for data in self._data:
            df = pd.concat([df, pd.json_normalize(data.__dict__)])
        df.set_index('frame_num', inplace=True)
