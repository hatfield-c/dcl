import pybullet as pb
import time
import pybullet_data

import SimpleDrone

physicsClient = pb.connect(pb.GUI)#or pb.DIRECT for non-graphical version
pb.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally
pb.setGravity(0,0,-10)

planeId = pb.loadURDF("plane.urdf")

startPos = [0,0,1]
#startOrientation = pb.getQuaternionFromEuler([0,0,0])

#drone_id = pb.loadURDF("drone_simple.urdf", startPos, startOrientation)
drone_urdf = "drone_simple.urdf"
drone = SimpleDrone.SimpleDrone(
	urdf_name = drone_urdf,
	position = startPos
)

for i in range (10000):
	drone.TakeAction()
	
	pb.stepSimulation()
	time.sleep(1./240.)
	
cubePos, cubeOrn = pb.getBasePositionAndOrientation(drone.pb_id)
print(cubePos,cubeOrn)

pb.disconnect()
