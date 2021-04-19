import cv2

from ._base_usecase import BaseUsecase
from ..domain.entity import BoardField, FieldManager, NextField, ScoreField


class GetScoreUsecase(BaseUsecase):
    def __init__(self, input_path: str):
        super().__init__()
        self._cap = cv2.VideoCapture(input_path)

    def run(self):
        while self._cap.isOpened():
            _, frame = self._cap.read()
            field_manager = FieldManager(frame)

            # 試合開始時に初期化
            if field_manager.is_game_break():
                # TODO フレームを巻き戻す

                # TODO 試合終了時のスコアを取得
                pass