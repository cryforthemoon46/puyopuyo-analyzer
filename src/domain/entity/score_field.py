import cv2
import numpy as np

from ..service import calc_zncc

TEMPLATE_CROSS = [cv2.imread('./assets/cross1.jpg'),
                  cv2.imread('./assets/cross2.jpg')]


class ScoreField:
    """
    得点画像とそれを用いた処理を集約したクラス
    """
    _ZNCC_THRESHOLD = 0.5  # ぷよとは違う閾値を使いたいので、クラス変数として定義

    def __init__(self):
        self._frame_history = []  # フレーム毎に「×」が見えているかを格納

    def forward(self, img: np.ndarray):
        # 8桁分の画像を1桁ずつに分割し、リストに格納する
        digits = [img[:, i * 27: (i + 1) * 27] for i in range(8)]

        # 発火時は左から5桁目が「×」になることを用いる
        zncc = max([calc_zncc(digits[4], i) for i in TEMPLATE_CROSS])
        self._frame_history.append(zncc > self._ZNCC_THRESHOLD)

        # 最後の2フレームだけ保持する
        self._frame_history = self._frame_history[-2:]

    @property
    def is_chain(self) -> bool:
        return self._frame_history[-1] and not self._frame_history[-2]
