# sumodgclass.py
# Author: Quentin Goss
# Last Modified: 3/27/18
# Class for SUMO directed graphs
class edge:
    def __init__(self):
        self.priority = None
        self._type = None
        self.lanes = None
        self.speed = 0.0
        self.length = 0.0
        self.id_me = None
        self.id_from = None
        self.id_to = None
        self.coords_true = None
        self.coords_norm = None

class vertex:
    def __init(self):
        self.id = None
        self.coords_true = None
        self.coords_norm = None
