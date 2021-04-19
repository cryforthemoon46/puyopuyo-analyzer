import cv2

from config import *
from ._base_usecase import BaseUsecase
from ..domain.entity import BoardField, FieldManager, NextField, ScoreField


class RealtimeChainAnalysisUsecase(BaseUsecase):
    def __init__(self, width: int = 1280, height: int = 720):
        super().__init__()
        self._cap = cv2.VideoCapture(1)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def run(self):
        while True:
            _, frame = self._cap.read()
            self._field_manager.forward(frame)

            # 試合開始時に初期化
            if self._field_manager.is_game_break():
                self._board_fields = {1: BoardField(), -1: BoardField()}
                self._next_fields = {1: NextField(self._fps),
                                     -1: NextField(self._fps)}
                self._score_fields = {1: ScoreField(), -1: ScoreField()}

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

            cv2.imshow('PuyoPuyo Analyzer: Realtime Chain Analysis', frame)
            if cv2.waitKey(15) & 0xFF == ord('q'):
                break

        self._cap.release()
        cv2.destroyAllWindows()
