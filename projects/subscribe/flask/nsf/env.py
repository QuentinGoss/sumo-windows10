import matplotlib.pyplot as plt
import nashpy
import numpy as np
from player import Player
from random import randrange
from threading import Thread
#create a environment to randomly set players locations
class Environment(object):
	def __init__(self):
		self.player_list = []
		for i in range(10):
			t = Thread(target=Player, args=(randrange(100), randrange(100))).start()


if __name__ == '__main__':
	env = Environment()