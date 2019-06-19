import numpy as np
import matplotlib.pyplot as plt
#import seaborn
import json
class DataCapture(object):
	def __init__(self, row, column, json_file = None):
		self.player_list = []
		self.row = row
		self.column = column
	def calculate_coverage(self):
		pass

	#here return all the player locations at each simulation step for replay
	def step(self):
		pass


