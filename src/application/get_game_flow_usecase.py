import cv2
from tqdm import tqdm

from config import *
from ._base_usecase import BaseUsecase
from ..domain.entity import BoardField, FieldManager, GameFlowData, NextField, \
    ScoreField
from ..domain.value import AttackData


class GetGameFlowUsecase(BaseUsecase):
    def __init__(self, input_path: str):
        super().__init__()
        self._attack_data = {PLAYER1: AttackData(1), PLAYER2: AttackData(1)}
        self._game_flow_data = GameFlowData()

        self._cap = cv2.VideoCapture(input_path)
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def run(self):
        for frame_num in tqdm(range(self._total_frames)):
            _, frame = self._cap.read()
            self._field_manager.forward(frame)

            # 試合開始時に初期化
            if self._field_manager.is_game_break():
                # 前試合情報を出力
                self._game_flow_data.process()

                self._is_valid = True
                self._board_fields = {1: BoardField(), -1: BoardField()}
                self._next_fields = {1: NextField(self._fps),
                                     -1: NextField(self._fps)}
                self._score_fields = {1: ScoreField(), -1: ScoreField()}
                self._game_flow_data = GameFlowData()

            # 試合開始前・発火後はキャプチャしないようにする
            if not self._is_valid:
                continue

            for player_num in [PLAYER1, PLAYER2]:
                # ネクスト領域を1フレーム進める
                next_field_img = self._field_manager.get_next_field(player_num)
                self._next_fields[player_num].forward(next_field_img)
                is_drawing = self._next_fields[player_num].is_drawing

                # 盤面領域を1フレーム進める
                board_field_img = self._field_manager.get_board_field(
                    player_num)
                self._board_fields[player_num].forward(board_field_img)

                # 得点領域を1フレーム進める
                score_field_img = self._field_manager.get_score_field(
                    player_num)
                self._score_fields[player_num].forward(score_field_img)
                is_chain = self._score_fields[player_num].is_chain

                # ツモる度に攻撃情報を初期化する
                if is_drawing:
                    self._board_fields[player_num].update_status()

                    # 攻撃終了後であれば保存
                    if self._attack_data[player_num].is_valid:
                        self.save_attack_data(frame_num, player_num)

                        # おじゃまぷよについて計算する
                        nuisance_count = \
                            self._board_fields[player_num].nuisance_count
                        if nuisance_count > 0:
                            nuisance_data = AttackData(2)
                            nuisance_data.frame_num = frame_num
                            nuisance_data.end_frame_num = frame_num
                            nuisance_data.nuisance = player_num
                            nuisance_data.nuisance_count = nuisance_count
                            self._game_flow_data.append(nuisance_data)

                    # 新しいオブジェクトを作成する
                    self._attack_data[player_num] = AttackData(1)

                # 連鎖時の処理
                if is_chain:
                    self._board_fields[player_num].update_status()
                    self.chain_process(frame_num, player_num)

            cv2.imshow('PuyoPuyo Analyzer: Get Game Flow', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self._cap.release()
        cv2.destroyAllWindows()

    def chain_process(self, frame_num, player_num):
        # データを有効にする
        self._attack_data[player_num].is_valid = True

        # 連鎖開始時のフレーム番号を記録する
        if not self._attack_data[player_num].frame_num:
            self._attack_data[player_num].frame_num = frame_num

        # プレイヤー番号を記録する
        if not self._attack_data[player_num].player_num:
            self._attack_data[player_num].player_num = player_num

        # 連鎖数を増やす
        self._attack_data[player_num].chain_num += 1

        # 消したぷよの数を加算する（おじゃまぷよは含めない）
        self._attack_data[player_num].eliminated_num += \
            len(self._board_fields[player_num].get_disappearing_puyo())

        # ラリーのスタートかを判定する
        if self._attack_data[player_num * -1].is_valid and \
                self._attack_data[player_num].is_start < 0:
            self._attack_data[player_num].is_start = 0
        elif not self._attack_data[player_num * -1].is_valid and \
                self._attack_data[player_num].is_start < 0:
            self._attack_data[player_num].is_start = 1

    def save_attack_data(self, frame_num: int, player_num: int):
        # 攻撃終了時のフレーム数を記録
        self._attack_data[player_num].end_frame_num = frame_num

        # 本線かどうか判定する
        is_main_chain = False
        if str(self._board_fields[player_num])[
           0: BOARD_ROW * BOARD_COLUMN: BOARD_ROW].count('-') > 0:
            is_main_chain = True

        # 本線回収率を算出する
        if is_main_chain:
            self._attack_data[player_num].is_main_chain = True
            rest = len(self._board_fields[player_num])
            eliminated = self._attack_data[player_num].eliminated_num
            self._attack_data[player_num].eliminated_percentage = \
                eliminated / (eliminated + rest)
        else:
            self._attack_data[player_num].is_main_chain = False

        # 攻撃情報を保存
        self._game_flow_data.append(self._attack_data[player_num])
