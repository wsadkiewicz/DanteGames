import pickle

class NetworkPacket:
    def __init__(self, packet_type, player_id=None, input_data=None, player_color=None, state_data=None):
        self.packet_type = packet_type
        self.player_id = player_id
        self.input_data = input_data or {}
        self.player_color = player_color
        self.state_data = state_data

    def to_bytes(self):
        return pickle.dumps(self)

    @staticmethod
    def from_bytes(data):
        return pickle.loads(data)