from config import *
from puyo import Puyo


class NextField:
    """
    ネクストぷよのデータとネクストぷよを使った処理を集約したクラス
    """

    def __init__(self):
        self._frame_history = []
        self.history = ''
        self.is_drawing = False

    def _get_tsumo(self):
        for i in reversed(range(len(self._frame_history) - 3)):
            if self._frame_history[i].find('-') < 0:
                return self._frame_history[i]

    def forward(self, img):
        """
        1フレーム進むに連れた処理を集約
        :param img: あるフレームをキャプチャした画像
        :return:
        """
        puyo1 = Puyo(img[PUYO_HEIGHT:, :])
        puyo2 = Puyo(img[:PUYO_HEIGHT, :])

        setting_puyo = str(puyo1) + str(puyo2)
        self._frame_history.append(setting_puyo)

        # 序盤は3フレーム分存在しないので処理を飛ばす
        if len(self._frame_history) < 6:
            self.is_drawing = False
            return

        # 現在のフレームから3フレーム連続でぷよがセットされていなかったらツモっていると判定
        for i in range(-1, -7, -1):
            if self._frame_history[i] != '--':
                self.is_drawing = False
                return
        self.is_drawing = True

        # その前にセットされていたツモを取得し、履歴に追加
        tsumo = self._get_tsumo()
        if tsumo:  # tsumoがNoneの場合（試合開始前など）は処理を飛ばす
            self.history += tsumo

        # 次のフレームでツモった判定にならないように空にする
        self._frame_history = []
