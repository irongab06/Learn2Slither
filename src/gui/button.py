import pygame

class bouton:
	def __init__(self, path_img_norm, path_img_hover, position, size) :
		self.normal_img = path_img_norm
		self.hover_img = path_img_hover
		self.current_img = self.normal_img
		self.rect = position