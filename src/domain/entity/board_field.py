import numpy as np
from collections import deque
from typing import List

from config import *
from ..value import Puyo


def extract_puyo(img: np.ndarray, i: int, j: int) -> np.ndarray:
    return img[PUYO_HEIGHT * i:PUYO_HEIGHT * (i + 1),
           PUYO_WIDTH * j:PUYO_WIDTH * (j + 1)]


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


def coordinate2offset(coordinate: List) -> int:
    """
    座標をoffsetに変換する
    :param coordinate:
    :return:
    """
    i, j = coordinate
    return j * BOARD_ROW + i


def offset2coordinate(offset: int) -> List:
    """
    offsetを座標に変換する
    :param offset:
    :return:
    """
    i = offset % BOARD_ROW
    j = int(offset / BOARD_ROW)
    return [i, j]


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

    def __len__(self):
        # おじゃまぷよ以外のぷよの数を返す
        return BOARD_ROW * BOARD_COLUMN - self._current_status.count(
            '-') - self._current_status.count('n')

    def __str__(self):
        return self._current_status

    @property
    def nuisance_count(self):
        return self._current_status.count('n')

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

    def get_disappearing_puyo(self):
        disappearing_puyo = []
        visited = []
        for j in range(BOARD_COLUMN):
            for i in range(BOARD_ROW):
                offset = coordinate2offset([i, j])
                target_puyo = self._current_status[offset]
                if target_puyo == '-' or target_puyo == 'n':
                    break
                connected_puyo, visited = self._get_connected_puyo(offset,
                                                                   visited)
                if len(connected_puyo) < 4:
                    continue
                disappearing_puyo += connected_puyo
        return disappearing_puyo

    def _get_connected_puyo(self, offset: int, visited: List):
        connected_puyo_lst = [offset]
        target_puyo = self._current_status[offset]
        queue = deque([offset2coordinate(offset)])
        while len(queue) > 0:
            ci, cj = queue.popleft()
            c_offset = coordinate2offset([ci, cj])
            visited.append(c_offset)
            for ni, nj in [(ci - 1, cj), (ci, cj + 1), (ci + 1, cj),
                           (ci, cj - 1)]:
                if nj < 0 or nj > 5 or ni < 0 or ni > 11:
                    continue

                n_offset = coordinate2offset([ni, nj])

                # 探索済の場合処理を飛ばす
                if n_offset in visited:
                    continue

                # 連結していない場合、処理を飛ばす
                if self._current_status[n_offset] != target_puyo:
                    continue

                connected_puyo_lst.append(n_offset)
                queue.append([ni, nj])

        return connected_puyo_lst, visited

    def update_status(self):
        self._previous_status = self._current_status
        count = 1
        current_status = '-' * 72
        i = -1
        while len(self._frame_history) > i * -1 and count < self._threshold:
            tmp_str = img2str(self._frame_history[i])
            if current_status == tmp_str:
                count += 1
            else:
                current_status = tmp_str
                count = 1
            i -= 1
        self._current_status = current_status
