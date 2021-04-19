from abc import ABCMeta, abstractmethod
import cv2

from ..domain.entity import FieldManager


class BaseUsecase(metaclass=ABCMeta):
    def __init__(self):
        self._is_valid = False
        self._field_manager = FieldManager()
        self._board_fields = None
        self._next_fields = None
        self._score_fields = None

    @abstractmethod
    def run(self):
        pass
