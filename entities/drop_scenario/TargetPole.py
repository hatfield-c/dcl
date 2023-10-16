import time
import random
import numpy as np
import pybullet as pb

import entities.SimpleEntity as SimpleEntity

class TargetPole(SimpleEntity.SimpleEntity):
	def __init__(
			self,
			pole_urdf,
			target_urdf,
			target_width,
			target_height,
			position = [0, 0 ,0],
			rotation = [0, 0, 0],
			quaternion = None,
			velocity = [0, 0, 0],
			angular_velocity = [0, 0 ,0],
			permuters = None,
			is_static = False,
		):
		self.pole_urdf = pole_urdf
		self.target_urdf = target_urdf

		super(TargetPole, self).__init__(self.pole_urdf, position, rotation, quaternion, velocity, angular_velocity, is_static, permuters)

		self.target_height = target_height
		self.target_width = target_width

		target_position = position

		target_position[0] = position[0] + target_width
		target_position[2] = position[2] + target_height

		self.target = SimpleEntity.SimpleEntity(
			target_urdf,
			target_position,
			self.GetRotation(),
			is_static = True
		)
