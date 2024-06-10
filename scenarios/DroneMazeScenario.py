
import time
import random
import math
import pybullet as pb
import numpy as np
import cv2

import scenarios.ScenarioInterface as ScenarioInterface
import scenarios.permuters.BoxPermuter as BoxPermuter

import physics.SimpleCounter as SimpleCounter
import render.RenderCamera as RenderCamera

import entities.SimpleEntity as SimpleEntity

import planners.PidAlignmentPlanner as PidAlignmentPlanner

import observers.HitPolyObserver as HitPolyObserver

class DroneMazeScenario(ScenarioInterface.ScenarioInterface):
	def __init__(
			self,
			client_id,
			gravity_strength,
			max_episodes,
			episode_length
		):
		self.client_id = client_id
		self.render_scenario = True

		if client_id != 0:
			self.render_scenario = False

		self.max_episodes = max_episodes
		self.episode_length = episode_length

		self.avg_episode_time = 0
		self.episode_time_start = time.time()

		self.time_counter = SimpleCounter.SimpleCounter(-1)
		self.episode_counter = SimpleCounter.SimpleCounter(-1)

		pb.setGravity(0, 0, -gravity_strength)

		self.agents = {}
		self.dynamic_objects = {}
		self.static_objects = {}
		self.unified_entities = {}
		self.visual_objects = {}
		self.observers = {}

		self.camera = RenderCamera.RenderCamera(self.client_id, pitch = -20, yaw = 0)
		self.camera.SetCamera([0, -5, 3])

	def ResetScenario(self):
		for pb_id in self.unified_entities:
			entity = self.unified_entities[pb_id]
			permutation_data = entity.GetStatePermutation()

			entity.SetState(permutation_data)

		self.time_counter.Reset()
		self.episode_counter.Increment()

	def ResetObservers(self):
		pass

	def RandomEnvGrid(self, density):
		env_grid = np.zeros((density[0], density[1], density[2]))
		
		x_indices = np.arange(1, density[0] - 1, 3)
		z_indices = np.arange(1, density[2] - 1, 3)
		
		for i in range(3, density[1] - 3, 7):
			#doors_x = np.random.randint(density[0], size = (2,))
			#doors_z = np.random.randint(density[2], size = (2,))
			
			doors_x = np.random.choice(x_indices, size = (2,), replace = False)
			doors_z = np.random.choice(z_indices, size = (2,), replace = False)
			
			env_grid[:, i, :] = 1
			
			for j in range(doors_x.shape[0]):
				door_x = doors_x[j]
				door_z = doors_z[j]
				
				env_grid[
					door_x - 1: door_x + 2, 
					i, 
					door_z - 1: door_z + 2, 
				] = 0
				
		return env_grid

	def CountGridCost(self, env_grid):
		grid_cost = np.ones(env_grid.shape)
		neighbor_indices = [-1, 0, 1]
		
		for i in range(env_grid.shape[0]):
			for j in range(env_grid.shape[1]):
				for k in range(env_grid.shape[2]):
					position = (i, j, k)
					
					area_count = 0
					for x in neighbor_indices:
						for y in neighbor_indices:
							for z in neighbor_indices:
								ix = i + x
								jy = j + y
								kz = k + z
								
								if ix < 0 or ix >= env_grid.shape[0] or jy < 0 or jy >= env_grid.shape[1] or kz < 0 or kz >= env_grid.shape[2]:
									area_count += 5
									continue
								
								if env_grid[ix, jy, kz] == 1:
									area_count += 5
									
					grid_cost[position] = area_count
										
		return grid_cost

	def InstantiateWalls(self, env_grid, density, origin, cell_size):
		for i in range(density[0]):
			print(i)
			for j in range(density[1]):
				for k in range(density[2]):
					is_occupied = env_grid[i, j, k]
					position = (
						(i * cell_size) + origin[0],
						(j * cell_size) + origin[1],
						(k * cell_size) + origin[2]
					)
					
					if is_occupied == 1:				
						cube = SimpleEntity.SimpleEntity(
							urdf_name = "entity_files/simple/1m_cube_static.urdf",
							client_id = self.client_id,
							is_static = True,
							position = position
						)
						
						self.visual_objects[(i,j,k)] = cube
						
	def InstantiatePath(self, path, origin, cell_size):
		for i in range(len(path)):
			grid_position = path[i]
			
			position = (
				(grid_position[0] * cell_size) + origin[0],
				(grid_position[1] * cell_size) + origin[1],
				(grid_position[2] * cell_size) + origin[2]
			)
		
			cube = SimpleEntity.SimpleEntity(
				urdf_name = "entity_files/simple/1m_cube_hitless_green.urdf",
				client_id = self.client_id,
				is_static = True,
				position = position
			)
			
			self.visual_objects[position] = cube

	def InstantiateEntities(self):

		density = (30, 50, 10)
		origin = (-15, 0, 0)
		start = (15, 0, 5)
		goal = (15, 49, 5)

		cell_size = 1
		env_grid = self.RandomEnvGrid(density)
		grid_cost = self.CountGridCost(env_grid)

		self.InstantiateWalls(env_grid, density, origin, cell_size)

		path = self.Astar(env_grid, grid_cost, start, goal)
		
		if path is None:
			print("[WARNING]: Null path generated!")
			input()
		
		self.InstantiatePath(path, origin, cell_size)

		self.UnifyEntities()

	def Heuristic(self, x1, x2):
		x1 = np.array(x1)
		x2 = np.array(x2)
		
		return np.linalg.norm(x2 - x1)

	def Astar(self, env_grid, grid_cost, start, goal):
		search_list = { start: start }
		best_predecessor = { start: None }
		cumulative_cost = { start: 0 }
		estimated_cost = { start: self.Heuristic(start, goal) }
	
		neighbor_indices = [-1, 0, 1]
		farthest_y = 0
		
		while len(search_list) > 0:
			current_position = min(search_list, key = cumulative_cost.get)
			
			if current_position[1] > farthest_y:
				print(current_position)
				farthest_y = current_position[1]
			
			if current_position == goal:
				break
			
			search_list.pop(current_position)
			
			for i in neighbor_indices:
				for j in neighbor_indices:
					for k in neighbor_indices:
						if i == 0 and j == 0 and k == 0:
							continue
						
						neighbor = (
							current_position[0] + i,
							current_position[1] + j,
							current_position[2] + k,
						)
						
						if neighbor[0] < 0 or neighbor[0] >= env_grid.shape[0] or neighbor[1] < 0 or neighbor[1] >= env_grid.shape[1] or neighbor[2] < 0 or neighbor[2] >= env_grid.shape[2]:
							continue
						
						if env_grid[neighbor] == 1:
							continue
			
						if neighbor not in cumulative_cost:
							cumulative_cost[neighbor] = 1e10
							estimated_cost[neighbor] = 1e10
						
						neighbor_cost = cumulative_cost[current_position] + grid_cost[neighbor]
						
						if neighbor_cost < cumulative_cost[neighbor]:
							best_predecessor[neighbor] = current_position
							cumulative_cost[neighbor] = neighbor_cost
							estimated_cost[neighbor] = neighbor_cost + self.Heuristic(neighbor, goal)
							
							if neighbor not in search_list:
								search_list[neighbor] = neighbor
		
		print("A star complete")
		
		if goal not in best_predecessor:
			return None
		
		current_position = goal
		total_path = [current_position]
		
		while current_position is not None:
			current_position = best_predecessor[current_position]
			total_path.insert(0, current_position)
			
		total_path.pop(0)
			
		return total_path
		
	def UnifyEntities(self):
		for agent_id in self.agents:
			agent = self.agents[agent_id]

			self.unified_entities[agent.GetBulletId()] = agent

		for dynamic_obj_id in self.dynamic_objects:
			dynamic_object = self.dynamic_objects[dynamic_obj_id]

			self.unified_entities[dynamic_object.GetBulletId()] = dynamic_object

		for static_obj_id in self.static_objects:
			static_object = self.static_objects[static_obj_id]

			self.unified_entities[static_object.GetBulletId()] = static_object

	def UpdateEntities(self):
	
		for entity_id in self.unified_entities:
			entity = self.unified_entities[entity_id]

			entity.UpdateEntity()

	def UpdateAgents(self):

		for agent_id in self.agents:
			agent = self.agents[agent_id]

			agent.ApplyDrag()
			agent.TakeAction()

	def UpdateObservers(self):
		for observer_name in self.observers:
			observer = self.observers[observer_name]
			observer.Observe(self.time_counter.GetCount())

	def ProcessEvents(self):
		pass

	def Render(self):

		if self.render_scenario:
			self.camera.FollowTarget()

	def UpdateTime(self):
		self.time_counter.Increment()

		if self.episode_counter.GetCount() >= self.max_episodes:
			return False

		if self.time_counter.GetCount() % self.episode_length == 0:
			self.ResetObservers()
			self.ResetScenario()

		return True
