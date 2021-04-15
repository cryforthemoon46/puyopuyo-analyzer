import pandas as pd


class GameFlowData:
    def __init__(self):
        self._data = []

    def append(self, data):
        self._data.append(data)

    def process(self):
        # DataFrameに変換する
        cols = ['frame_num', 'end_frame_num', 'object_type', 'is_valid',
                'player_num', 'chain_num', 'is_main_chain', 'eliminated_num',
                'eliminated_percentage', 'nuisance', 'nuisance_count',
                'is_start']
        df = pd.DataFrame(index=[], columns=cols)
        for data in self._data:
            df = pd.concat([df, pd.json_normalize(data.__dict__)])

        # end_frame_numで昇順にsort
        df.sort_values('frame_num', inplace=True)

        # is_continue列をis_startと逆になるように初期化
        df['is_continue'] = 1 - df['is_start']

        # おじゃまぷよに対する処理を行う
        nuisance_df = df.loc[df['object_type'] == 2, :]
        nuisance_df.drop(
            ['end_frame_num', 'object_type', 'is_valid', 'player_num',
             'chain_num', 'is_main_chain', 'eliminated_num',
             'eliminated_percentage', 'is_start', 'is_continue'], axis=1,
            inplace=True)
        for row in nuisance_df.itertuples():
            df.loc[df['end_frame_num'] == row.frame_num, 'is_continue'] = 0

        # 不要な列を削除する
        df.drop(['is_valid', 'eliminated_num'], axis=1, inplace=True)

        # frame_numの順番にソート
        # df.sort_values('frame_num', inplace=True)

        print(df)
