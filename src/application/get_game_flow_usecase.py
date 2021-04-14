import cv2
from tqdm import tqdm

from config import *
from ._base_usecase import BaseUsecase
from ..domain.entity import BoardField, FieldManager, NextField, ScoreField
from ..domain.value import AttackData


class GetGameFlowUsecase(BaseUsecase):
    def __init__(self, input_path):
        super().__init__(input_path)
        self._attack_data = {PLAYER1: AttackData(), PLAYER2: AttackData()}

    def run(self):
        for frame_num in tqdm(range(self._total_frames)):
            _, frame = self._cap.read()
            field_manager = FieldManager(frame)

            # 試合開始時に初期化
            if field_manager.is_game_start():
                # 前試合情報を出力

                self._is_valid = True
                self._board_fields = {1: BoardField(), -1: BoardField()}
                self._next_fields = {1: NextField(self._fps),
                                     -1: NextField(self._fps)}
                self._score_fields = {1: ScoreField(), -1: ScoreField()}

            # 試合開始前・発火後はキャプチャしないようにする
            if not self._is_valid:
                continue

            for player_num in [PLAYER1, PLAYER2]:
                # ネクスト領域を1フレーム進める
                next_field_img = field_manager.get_next_field(player_num)
                self._next_fields[player_num].forward(next_field_img)
                is_drawing = self._next_fields[player_num].is_drawing

                # 盤面領域を1フレーム進める
                board_field_img = field_manager.get_board_field(player_num)
                self._board_fields[player_num].forward(board_field_img)

                # 得点領域を1フレーム進める
                score_field_img = field_manager.get_score_field(player_num)
                self._score_fields[player_num].forward(score_field_img)
                is_chain = self._score_fields[player_num].is_chain

                # ツモる度に攻撃情報を初期化する
                if is_drawing:
                    self._board_fields[player_num].update_status()

                    if self._attack_data[player_num].is_valid:
                        self.save_attack_data(player_num)

                    self._attack_data[player_num] = AttackData()

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

    def save_attack_data(self, player_num):
        print()
        print(self._attack_data[player_num].__dict__)
