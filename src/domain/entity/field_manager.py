import cv2
import numpy as np
from typing import Tuple

from config import *


def find_board_x(img: np.ndarray) -> Tuple[dict, dict]:
    """
    各プレイヤーの盤面のx座標を求める
    :param img:
    :return:
    """
    tmp_xmin = 640
    tmp_xmax = 640

    # エッジ検出
    frame_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    frame_blur = cv2.GaussianBlur(frame_gray, (5, 5), 0)
    frame_edge = cv2.Canny(frame_blur, 50, 100)

    # ハフ変換による直線検出。x座標の最小値を1P盤面の左端、最大値を2P盤面の右端とする。
    lines = cv2.HoughLines(frame_edge, 1, np.pi / 2, 200)
    try:
        for line in lines:
            rho, theta = line[0]
            # 縦線のみ検出する
            if theta != 0:
                continue
            x = np.cos(theta) * rho
            tmp_xmin = min(tmp_xmin, x) if x > 150 else tmp_xmin
            tmp_xmax = max(tmp_xmax, x) if x < 1130 else tmp_xmax

        # int型への変換と、盤面内側を検出するための補正
        player1_field_xmin = int(tmp_xmin) + 17
        player1_field_xmax = player1_field_xmin + PUYO_WIDTH * BOARD_COLUMN
        player2_field_xmax = int(tmp_xmax) - 18
        player2_field_xmin = player2_field_xmax - PUYO_WIDTH * BOARD_COLUMN
        return {1: player1_field_xmin, -1: player2_field_xmin}, {
            1: player1_field_xmax, -1: player2_field_xmax}

    # linesが見つからなかったときの対策
    except TypeError:
        return {1: 186, -1: 836}, {1: 444, -1: 1094}


class FieldManager:
    """
    各フレーム時の画面全体と、各領域を切り出すメソッドを集約したクラス
    """
    _BLACKOUT_THRESHOLD = 32
    _NEXT_AREA_YMIN = 108
    _NEXT_AREA_YMAX = 188
    _NEXT_AREA_XMIN = {1: 480, -1: 757}
    _NEXT_AREA_XMAX = {1: 523, -1: 800}
    _SCORE_AREA_YMIN = 590
    _SCORE_AREA_YMAX = 626
    _SCORE_AREA_XMIN = {1: 233, -1: 831}
    _SCORE_AREA_XMAX = {1: 449, -1: 1047}
    _BOARD_AREA_YMIN = 106
    _BOARD_AREA_YMAX = 586

    def __init__(self):
        self._prev_frame = None
        self._frame = None
        self._board_area_xmin, self._board_area_xmax = None, None

    def forward(self, frame: np.ndarray):
        self._prev_frame = self._frame
        self._frame = frame
        self._board_area_xmin, self._board_area_xmax = find_board_x(frame)

    def get_next_field(self, player_num: int) -> np.ndarray:
        return self._frame[
               self._NEXT_AREA_YMIN:self._NEXT_AREA_YMAX,
               self._NEXT_AREA_XMIN[player_num]:self._NEXT_AREA_XMAX[player_num]
               ]

    def get_score_field(self, player_num: int) -> np.ndarray:
        return self._frame[
               self._SCORE_AREA_YMIN:self._SCORE_AREA_YMAX,
               self._SCORE_AREA_XMIN[player_num]:self._SCORE_AREA_XMAX[
                   player_num]
               ]

    def get_board_field(self, player_num: int) -> np.ndarray:
        return self._frame[
               self._BOARD_AREA_YMIN:self._BOARD_AREA_YMAX,
               self._board_area_xmin[player_num]:self._board_area_xmax[
                   player_num]
               ]

    def is_game_break(self) -> bool:
        if not isinstance(self._prev_frame, np.ndarray):
            return False
        return np.mean(self._frame) < self._BLACKOUT_THRESHOLD <= np.mean(
            self._prev_frame)
