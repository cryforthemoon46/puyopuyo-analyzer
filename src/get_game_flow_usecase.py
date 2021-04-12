import cv2
import numpy as np
from tqdm import tqdm

from _base_usecase import BaseUsecase
from board_field import BoardField
from field_manager import FieldManager
from next_field import NextField
from score_field import ScoreField


class GetGameFlowUsecase(BaseUsecase):
    def run(self):
        for frame_num in tqdm(range(self._total_frames)):
            _, frame = self._cap.read()
            field_manager = FieldManager(frame)

            # 試合開始時に初期化
            # 試合開始時に初期化
            if field_manager.is_game_start():
                # 前試合情報を出力

                self._is_valid = True
                self._board_fields = {1: BoardField(), -1: BoardField()}
                self._next_fields = {1: NextField(), -1: NextField()}
                self._score_fields = {1: ScoreField(), -1: ScoreField()}

            # 試合開始前・発火後はキャプチャしないようにする
            if not self._is_valid:
                continue

            cv2.imshow('PuyoPuyo Analyzer - Get Game Flow', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self._cap.release()
        cv2.destroyAllWindows()
