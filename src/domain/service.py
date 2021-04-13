import cv2
import numpy as np

from config import *


def calc_zncc(roi_img: np.ndarray, tpl_img: np.ndarray) -> float:
    """
    :param roi_img: ぷよ画像
    :param tpl_img: テンプレート画像
    :return: 2つの画像の類似度 (ZNCC)
    """
    roi_h, roi_w = roi_img.shape[:2]
    roi_img = np.array(roi_img, dtype="float")
    roi_img -= np.mean(roi_img)

    tpl_img = cv2.resize(tpl_img, (roi_w, roi_h))
    tpl_img = np.array(tpl_img, dtype="float")
    tpl_img -= np.mean(tpl_img)

    numerator = np.sum(roi_img * tpl_img)
    denominator = np.sqrt(np.sum(roi_img ** 2)) * np.sqrt(
        np.sum(tpl_img ** 2))

    zncc = numerator / denominator if denominator != 0 else 0
    return zncc




