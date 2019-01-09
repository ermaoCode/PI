"""
A class represent fuzz model.

Including common fields, special fields(such as length field and checksum field)
Including a block layer.
Written by Jennings Mao <maojianling@ict.ac.cn>
"""
class ProtocolField:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length



class FuzzModel:
    def __init__(self, mutate_list):
        self._mutate_list = mutate_list
        self.len = len(mutate_list)


    def parse_structure(self):

