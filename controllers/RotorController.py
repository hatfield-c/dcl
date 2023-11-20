import pybullet as pb
import numpy as np
import math

import CONFIG
import physics.Transform as Transform
import controllers.ControllerInterface as ControllerInterface
import controllers.modules.Pid as Pid

class RotorController(ControllerInterface.ControllerInterface):
	def __init__(self):
		pass

	def GetControlSignal(self, plan, metadata):

		return plan
