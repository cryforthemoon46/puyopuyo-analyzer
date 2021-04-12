import cv2
import numpy as np

from utils import calc_zncc


class ScoreField:
    """
    得点画像とそれを用いた処理を集約したクラス
    """
    _TEMPLATE_CROSS = [cv2.imread('../assets/cross1.jpg'),
                       cv2.imread('../assets/cross2.jpg')]
    _ZNCC_THRESHOLD = 0.7  # ぷよとは違う閾値を使いたいので、クラス変数として定義

    def __init__(self):
        self._current_ren = 0
        self._frame_history = []  # フレーム毎に「×」が見えているかを格納
        self._ren_history = []
        self.is_firing = False

    @property
    def avg_ren(self):
        return sum(self._ren_history) / len(self._ren_history) if len(
            self._ren_history) > 0 else 0

    @property
    def max_ren(self):
        return max(self._ren_history) if len(self._ren_history) > 0 else 0

    def forward(self, img: np.ndarray, is_drawing: bool):
        self.is_firing = False

        # 8桁分の画像を1桁ずつに分割し、リストに格納する
        digits = [img[:, i * 27: (i + 1) * 27] for i in range(8)]

        # ツモる度に初期化する
        if is_drawing:
            if self._current_ren > 0:
                self._ren_history.append(self._current_ren)
                self._current_ren = 0
            return

        # 発火時は左から5桁目が「×」になることを用いる
        zncc = max([calc_zncc(digits[4], i) for i in self._TEMPLATE_CROSS])
        self._frame_history.append(zncc > self._ZNCC_THRESHOLD)

        # 「×」が表示された瞬間のみ発火・連鎖と認識する
        if self._frame_history[-1] and not self._frame_history[-2]:
            if self._current_ren == 0:
                self.is_firing = True
            self._current_ren += 1

        # 10フレーム分だけ保持する
        self._frame_history = self._frame_history[-20:]
