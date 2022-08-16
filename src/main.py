from UnicodeEngine_RPG import UnicodeEngine_RPG, Char, Player, getch, InventoryItem
from typing import Union
import colorama; colorama.init()
from colorama import Fore, Back, Style
import os
import json

from perlin_numpy import generate_perlin_noise_2d


class Game:
	def __init__(self, playable_area_size:int=32):
		"""
		Initializes the main game class.
		:param playable_area_size: The size of the playable area. MUST BE A MULTIPLE OF 2 !
		"""
		self.playable_area_size = playable_area_size
		self.chars = {
			"desolated_river": Char("░"),
			"desolated_land": Char("▒"),
			"desolated_hilltop": Char("▓")
		}
		self.tilemap = [[]]
		self.generate_tilemap()
		self.app = UnicodeEngine_RPG(
			tilemap=self.tilemap,
			player=Player([0, 0])
		)


	def generate_tilemap(self):
		"""
		Generates a random tilemap for the game and returns it
		"""
		# Generating a 32x32 (by default) terrain with random variation (noise)
		noise = generate_perlin_noise_2d((self.playable_area_size, self.playable_area_size), (2, 2))
		def calculate_height(x, z):
			# Calculates the height of the tile based off the noise map and its value
			val = noise[x + self.playable_area_size // 2][z + self.playable_area_size // 2]
			return_val = self.chars["desolated_land"]  # Initiated at 0, standard height
			if -0.06 < val < 0.06:  # River, one below
				return_val = self.chars["desolated_river"]
			elif val > 0.4:  # Cliff, one above
				return_val = self.chars["desolated_hilltop"]
			return return_val

		self.tilemap = [[calculate_height(x, z) for x in range(-self.playable_area_size // 2, self.playable_area_size // 2)] \
	           for z in range(-self.playable_area_size // 2, self.playable_area_size // 2)]
		return self.tilemap



	def update(self, dt: float):
		if self.app.keystroke == "g":
			self.generate_tilemap()
			self.app.tilemap = self.tilemap


	def run(self):
		self.app.run(self.update)



if __name__ == "__main__":
	game = Game()
	game.run()

