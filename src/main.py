from UnicodeEngine_RPG import UnicodeEngine_RPG, Char, Player, getch, InventoryItem
from typing import Union
import colorama; colorama.init()
from colorama import Fore, Back, Style
import os
import json


class Game:
	def __init__(self):
		self.tilemap = [[]]
		self.app = UnicodeEngine_RPG(
			tilemap=self.tilemap,
			player=Player([0, 0])
		)


	def update(self, dt: float):
		pass


	def run(self):
		self.app.run(self.update)



if __name__ == "__main__":
	game = Game()
	game.run()

