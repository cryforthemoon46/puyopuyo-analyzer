import numpy as np

from config import *
from puyo import Puyo


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


class BoardField:
    """
    盤面のデータとそれらを使った処理を集約したクラス
    """

    def __init__(self):
        self._frame_history = []  # NextAreaと異なり、画像データを格納
        self.history = []
        self.is_start = False

    def _get_current_status(self):
        """
        現在の盤面の状態を取得する
        3フレーム連続で同じ文字列だった場合に正しい盤面であると定義する
        :return:
        """
        count = 1
        current_status = '-' * 72
        i = -1
        while len(self._frame_history) > i * -1 and count < 6:
            tmp_str = img2str(self._frame_history[i])
            if current_status == tmp_str:
                count += 1
            else:
                current_status = tmp_str
                count = 1
            i -= 1
        return current_status

    def forward(self, img: np.ndarray, is_capture: bool):
        self._frame_history.append(img)

        # ツモった瞬間、発火した瞬間以外は処理を飛ばす
        if not is_capture:
            return

        # 盤面履歴を追加する
        self.history.append(self._get_current_status())

        # 1秒分だけ保持する
        self._frame_history = self._frame_history[-30:]

    def show(self):
        print('+------+')
        for i in reversed(range(BOARD_ROW)):
            print(f'|{self.history[-1][i::BOARD_ROW]}|')
        print('+------+')
        print()
