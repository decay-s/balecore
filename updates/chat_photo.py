class ChatPhoto:
    def __init__(self, small_file_id: str, big_file_id: str):
        self.small_file_id = small_file_id
        self.big_file_id = big_file_id

    def to_dict(self):
        return {
            "small_file_id": self.small_file_id,
            "big_file_id": self.big_file_id
        }