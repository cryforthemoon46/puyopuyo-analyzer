from abc import ABCMeta, abstractmethod
import cv2


class BaseUsecase(metaclass=ABCMeta):
    def __init__(self, input_path: str):
        self._is_valid = False
        self._board_fields = None
        self._next_fields = None
        self._score_fields = None

        self._cap = cv2.VideoCapture(input_path)
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @abstractmethod
    def run(self):
        pass
