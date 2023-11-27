import pybullet as pb
import numpy as np

FORWARD = np.array([0, 1, 0])
RIGHT = np.array([1, 0, 0])
UP = np.array([0, 0, 1])
BACKWARD = np.array([0, -1, 0])
LEFT = np.array([-1, 0, 0])
DOWN = np.array([0, 0, -1])

def GetUnit(vector):
	magnitude = np.linalg.norm(vector)

	if magnitude == 0:
		magnitude = 1

	return vector / magnitude

def RotationToDirection(rotation):
	x = -np.sin(rotation[2]) * np.cos(rotation[0])
	y = np.cos(rotation[2]) * np.cos(rotation[0])
	z = np.sin(rotation[0])

	direction = np.array([x, y, z])
	magnitude = np.linalg.norm(direction)

	return direction / magnitude

def RotatePoint(quaternion, point):
	rotate_matrix = pb.getMatrixFromQuaternion(quaternion)
	rotate_matrix = np.array(rotate_matrix)
	rotate_matrix = rotate_matrix.reshape((3, 3))

	point_rotated = np.matmul(rotate_matrix, point)

	return point_rotated

def RotateDirection(quaternion, direction):
	direction_rotated = RotatePoint(quaternion, direction)

	magnitude = np.linalg.norm(direction_rotated)
	if magnitude == 0:
		magnitude = 1

	return direction_rotated / magnitude

def GetForward(quaternion):
	return RotateDirection(quaternion, FORWARD)

def GetRight(quaternion):
	return RotateDirection(quaternion, RIGHT)

def GetUp(quaternion):
	return RotateDirection(quaternion, UP)

def GetBackward(quaternion):
	return RotateDirection(quaternion, BACKWARD)

def GetLeft(quaternion):
	return RotateDirection(quaternion, LEFT)

def GetDown(quaternion):
	return RotateDirection(quaternion, DOWN)
