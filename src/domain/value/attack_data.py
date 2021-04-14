class AttackData:
    def __init__(self, object_type):
        self.frame_num = None
        self.object_type = object_type  # 1: Attack Data, 2: Nuisance Data
        self.is_valid = False
        self.player_num = None
        self.chain_num = 0
        self.is_main_chain = False
        self.eliminated_num = 0
        self.eliminated_percentage = None
        self.nuisance = None
        self.nuisance_count = 0
        self.is_start = -1
