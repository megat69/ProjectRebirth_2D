from UnicodeEngine_RPG import UnicodeEngine_RPG, Char, Player, getch, InventoryItem
from typing import Union
import colorama; colorama.init()
from colorama import Fore, Back, Style
import os
import json
import sys
from math import sqrt

from perlin_numpy import generate_perlin_noise_2d
from tiles import Tile, Building

DEV_MODE = True


class Game:
	def __init__(self, playable_area_size:int=32):
		"""
		Initializes the main game class.
		:param playable_area_size: The size of the playable area. MUST BE A MULTIPLE OF 2 !
		"""
		self.playable_area_size = playable_area_size
		land_buildable = (
			"desolated_land",
			"desolated_hilltop",
			"undesolated_land",
			"undesolated_hilltop",
			"sane_land",
			"sane_hilltop"
		)
		def power_plant_action():
			for y, x in self.radius(self.get_player_pos(), 6, self.playable_area_size):
				if isinstance(self.tilemap[y][x], Tile):
					self.tilemap[y][x].powered = True
		def land_sanitizer_action():
			for y, x in self.radius(self.get_player_pos(), 4, self.playable_area_size):
				if isinstance(self.tilemap[y][x], Tile):
					if self.tilemap[y][x].char_name == "desolated_land":
						self.tilemap[y][x] = self.chars["undesolated_land"].copy().set_power(self.tilemap[y][x].powered)
					elif self.tilemap[y][x].char_name == "desolated_hilltop":
						self.tilemap[y][x] = self.chars["undesolated_hilltop"].copy().set_power(self.tilemap[y][x].powered)
		def water_pump_action(sublevel=0, pos=None):
			if pos is None:
				player_y, player_x = self.get_player_pos()
			else:
				player_y, player_x = pos
			for y, x in ((y, x) for x in range(-1, 2) for y in range(-1, 2)):
				try:
					tile = self.tilemap[player_y + y][player_x + x]
				except IndexError:
					continue
				else:
					if player_y + y < 0 or player_x + x < 0:
						continue
				if not isinstance(tile, Building) and tile.char_name == "desolated_river":
					self.tilemap[player_y + y][player_x + x] = self.chars["sane_river"].copy().set_power(tile.powered)
					if sublevel < 5:
						water_pump_action(sublevel+1, (player_y + y, player_x + x))
		def water_dispenser_action():
			for y, x in self.radius(self.get_player_pos(), 4, self.playable_area_size):
				if isinstance(self.tilemap[y][x], Tile):
					if self.tilemap[y][x].char_name == "undesolated_land":
						self.tilemap[y][x] = self.chars["sane_land"].copy().set_power(self.tilemap[y][x].powered)
					elif self.tilemap[y][x].char_name == "undesolated_hilltop":
						self.tilemap[y][x] = self.chars["sane_hilltop"].copy().set_power(self.tilemap[y][x].powered)
		self.chars = {
			# Tiles
			"desolated_river": Tile("desolated_river", "░"),
			"desolated_land": Tile("desolated_land", "▒"),
			"desolated_hilltop": Tile("desolated_hilltop", "▓"),
			"undesolated_land": Tile("undesolated_land", "▒", color=Back.LIGHTBLACK_EX),
			"undesolated_hilltop": Tile("undesolated_hilltop", "▓", color=Back.LIGHTBLACK_EX),
			"sane_river": Tile("sane_river", "░", color=Back.CYAN),
			"sane_land": Tile("sane_land", "▒", color=Back.GREEN),
			"sane_hilltop": Tile("sane_hilltop", "▓", color=Back.GREEN),

			# Buildings
			"Power plant": Building("P", position=2, buildable_on=land_buildable, build_action=power_plant_action),
			"Land sanitizer": Building("L", position=2, buildable_on=land_buildable, build_action=land_sanitizer_action),
			"Water pump": Building("W", position=2, buildable_on=("desolated_river", "sane_river"), build_action=water_pump_action),
			"Water dispenser": Building("D", position=2, buildable_on=land_buildable, build_action=water_dispenser_action)
		}
		self.tilemap = [[]]
		self.generate_tilemap()
		self.app = UnicodeEngine_RPG(
			tilemap=self.tilemap,
			player=Player([0, 0]),
			controls="zqsdf",
			inventory={
				"available_buildings": InventoryItem(
					"Available buildings",
					["Power plant", "Land sanitizer", "Water pump", "Water dispenser"],
					lambda e: e),
				"selected_building": InventoryItem("Selected building", "Power plant", lambda e: e)
			},
			playable_area=(14, 14)
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
			return_val = self.chars["desolated_land"].copy()  # Initiated at 0, standard height
			if -0.06 < val < 0.06:  # River, one below
				return_val = self.chars["desolated_river"].copy()
			elif val > 0.4:  # Cliff, one above
				return_val = self.chars["desolated_hilltop"].copy()
			return return_val

		self.tilemap = [[calculate_height(x, z) for x in range(-self.playable_area_size // 2, self.playable_area_size // 2)] \
	           for z in range(-self.playable_area_size // 2, self.playable_area_size // 2)]
		return self.tilemap


	@staticmethod
	def radius(position: tuple[int, int] | list[int, int], radius: int, playable_area_size: int):
		"""
		Yields a generator containing the coordinates of each tile withing the given radius.
		Automatically culls the tiles out of range.
		:param position: The position to start from.
		:param radius: The radius to look for.
		:param playable_area_size: The size of the playable area.
		"""
		for y in range(-radius, radius):
			# Culling the tiles out of range
			if y + position[0] < 0 or y + position[0] >= playable_area_size:
				continue
			for x in range(-radius, radius):
				# Culling the tiles out of range
				if x + position[1] < 0 or x + position[1] >= playable_area_size:
					continue

				# If in range, yielding the coordinates of the tile
				yield (position[0] + y, position[1] + x)


	def get_player_pos(self):
		"""
		Returns the player position as a tuple
		"""
		return tuple(self.app.player.position)


	def get_player_hovered_tile(self) -> Tile | Char:
		"""
		Returns the tile that is currently being selected by the player.
		"""
		return self.tilemap[self.app.player.position[0]][self.app.player.position[1]]


	def get_player_hovered_tile_name(self) -> str:
		"""
		Returns the name of the tile currently being selected by the player.
		"""
		tile = self.get_player_hovered_tile()
		if tile in tuple(self.chars[e] for e in ("Power plant", "Land sanitizer", "Water pump", "Water dispenser")):
			for name, instance in tuple((e, self.chars[e]) for e in ("Power plant", "Land sanitizer",
			                                                         "Water pump", "Water dispenser")):
				if tile == instance:
					return name
		else:
			return tile.char_name


	def get_selected_building(self) -> str:
		"""
		Returns the name of the selected building.
		"""
		return self.app.inventory["selected_building"].value


	def get_selected_building_char(self) -> Building:
		"""
		Returns the Char instance of the selected building.
		"""
		return self.chars[self.get_selected_building()]


	def update(self, dt: float):
		# Regenerating the tilemap IF IN DEV MODE ONLY
		if self.app.keystroke == "g" and DEV_MODE:
			self.generate_tilemap()
			self.app.tilemap = self.tilemap


		elif self.app.keystroke == "h" and DEV_MODE:
			print(self.get_player_hovered_tile().powered)

		# Placing the current building
		elif self.app.keystroke == self.app.controls[4]:
			# Building only if the player is on a zone the building can be built on
			if self.get_player_hovered_tile_name() in self.get_selected_building_char().buildable_on and \
					(self.get_player_hovered_tile().powered or self.get_selected_building() == "Power plant"):
				# Getting the player position
				player_y, player_x = self.get_player_pos()
				# Adding the building to the map
				self.tilemap[player_y][player_x] = self.get_selected_building_char()
				# Letting the building do its action
				self.get_selected_building_char().build_action()
				# Updating the tilemap
				self.app.tilemap = self.tilemap

		# Selecting another building
		elif self.app.keystroke.isdigit():
			ks = int(self.app.keystroke) - 1
			try:
				self.app.inventory["selected_building"].value = self.app.inventory["available_buildings"].value[ks]
			except IndexError:
				pass



	def run(self):
		self.app.run(self.update)



if __name__ == "__main__":
	game = Game()
	game.run()

