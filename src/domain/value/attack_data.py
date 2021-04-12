class AttackData:
    def __init__(self, frame_num: int, player_num: int):
        self.is_valid = False
        self.frame_num = frame_num
        self.player_num = player_num
        self.chain_num = 0
        self.is_main_chain = False
        self.eliminated_percentage = 0
