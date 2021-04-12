import numpy as np
from typing import List

from config import *
from ..value import Puyo


def extract_puyo(img: np.ndarray, i: int, j: int) -> np.ndarray:
    return img[PUYO_HEIGHT * i:PUYO_HEIGHT * (i + 1),
           PUYO_WIDTH * j:PUYO_WIDTH * (j + 1)]


def get_current_status(frame_history: List[np.ndarray]) -> str:
    """
    現在の盤面の状態を取得する
    3フレーム連続で同じ文字列だった場合に正しい盤面であると定義する
    :return:
    """
    count = 1
    current_status = '-' * 72
    i = -1
    while len(frame_history) > i * -1 and count < 6:
        tmp_str = img2str(frame_history[i])
        if current_status == tmp_str:
            count += 1
        else:
            current_status = tmp_str
            count = 1
        i -= 1
    return current_status


def img2str(img: np.ndarray):
    status_str = ''

    # 列ごとのほうが処理がしやすいためj->iの順でループ
    for j in range(BOARD_COLUMN):
        for i in reversed(range(BOARD_ROW)):
            puyo_type = str(Puyo(extract_puyo(img, i, j)))
            if puyo_type == '-':
                status_str += '-' * (i + 1)
                break
            status_str += puyo_type

    return status_str


class BoardField:
    """
    盤面のデータとそれらを使った処理を集約したクラス
    """

    def __init__(self, fps: int = 30):
        self._fps = fps
        self._frame_history = []  # NextAreaと異なり、画像データを格納
        self._threshold = int(fps / 10)
        self._previous_status = '-' * BOARD_ROW * BOARD_COLUMN
        self._current_status = '-' * BOARD_ROW * BOARD_COLUMN

    def forward(self, img: np.ndarray):
        self._frame_history.append(img)
        self._frame_history = self._frame_history[self._fps * -1:]

    def get_diff(self):
        diff = []
        for x in range(BOARD_ROW * BOARD_COLUMN):
            # 盤面に変化がない位置については処理を飛ばす
            if self._current_status[x] == self._previous_status[x]:
                continue

            puyo_type = self._current_status[x]
            i = x % BOARD_ROW
            j = int(x / BOARD_ROW)

            diff.append([puyo_type, i, j])

        return diff

    def get_disappearing(self):
        for i in range(BOARD_ROW):
            for j in range(BOARD_COLUMN):
                offset = BOARD_ROW * j + i

    def update_status(self):
        self._previous_status = self._current_status
        self._current_status = get_current_status(self._frame_history)
