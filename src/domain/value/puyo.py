import cv2
import numpy as np

from src.domain.service import calc_zncc

# 「/root」ディレクトリからの相対パスなので気をつける
TEMPLATES = {
    'r': cv2.imread('./assets/puyo_r.jpg'),
    'g': cv2.imread('./assets/puyo_g.jpg'),
    'b': cv2.imread('./assets/puyo_b.jpg'),
    'y': cv2.imread('./assets/puyo_y.jpg'),
    'p': cv2.imread('./assets/puyo_p.jpg'),
    'n': cv2.imread('./assets/puyo_n.jpg'),
    'n_s': cv2.imread('./assets/puyo_n_s.jpg'),
    'n_m': cv2.imread('./assets/puyo_n_m.jpg'),
}
ZNCC_THRESHOLD = 0.5


class Puyo:
    """
    ぷよの画像とその種類を出力するメソッドを集約したクラス
    """
    _ZNCC_THRESHOLD = 0.5

    def __init__(self, img: np.ndarray):
        self._img = img

    def __str__(self):
        inferred_puyo_type = '-'
        max_zncc = ZNCC_THRESHOLD
        for puyo_type, tpl_img in TEMPLATES.items():
            zncc = calc_zncc(self._img, tpl_img)
            if zncc > max_zncc:
                inferred_puyo_type = puyo_type
                max_zncc = zncc
        inferred_puyo_type = inferred_puyo_type.split('_')[
            0] if inferred_puyo_type != '-' else '-'
        return inferred_puyo_type
