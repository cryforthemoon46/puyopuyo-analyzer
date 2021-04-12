import cv2
from tqdm import tqdm

from config import *
from ._base_usecase import BaseUsecase
from ..domain.entity import BoardField, FieldManager, NextField, ScoreField
from ..domain.value import AttackData


class GetGameFlowUsecase(BaseUsecase):
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

                attack_data = {PLAYER1: None, PLAYER2: None}

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

                    # 有効なデータのみ出力
                    if attack_data[player_num] and \
                            attack_data[player_num].is_valid:
                        print()
                        print(attack_data[player_num].__dict__)

                    attack_data[player_num] = AttackData(frame_num, player_num)

                # 連鎖時の処理
                if is_chain:
                    self._board_fields[player_num].update_status()
                    attack_data[player_num].is_valid = True
                    attack_data[player_num].chain_num += 1

            cv2.imshow('PuyoPuyo Analyzer: Get Game Flow', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self._cap.release()
        cv2.destroyAllWindows()
