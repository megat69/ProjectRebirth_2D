from UnicodeEngine_RPG import Char
from copy import deepcopy
from typing import Callable
from colorama import Fore

VISUALIZE_POWER = False


class Tile(Char):
	def __init__(self, char_name:str, *args, powered:bool=False, **kwargs):
		super().__init__(*args, **kwargs)
		self._powered = powered
		self.char_name = char_name


	@property
	def powered(self):
		return self._powered

	@powered.setter
	def powered(self, value: bool):
		self._powered = value
		self.name = (Fore.LIGHTYELLOW_EX if self.powered and self.char_name != "sane_hilltop" and \
		                                    VISUALIZE_POWER else '')\
		            + self.name + (Fore.RESET if self.powered and VISUALIZE_POWER else '')


	def copy(self):
		return deepcopy(self)


	def set_power(self, powered:bool):
		"""
		Sets the power in the tile.
		:return: Returns self to allow for method chaining.
		"""
		self.powered = powered
		return self


class Building(Char):
	def __init__(self, *args, build_action:Callable=None, buildable_on:tuple=tuple(), **kwargs):
		super().__init__(*args, **kwargs)
		self.buildable_on = buildable_on
		self.build_action = build_action if build_action is not None else lambda: None


	def copy(self):
		return deepcopy(self)
