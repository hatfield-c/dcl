import pybullet as pb
import time
import pybullet_data

physicsClient = pb.connect(pb.GUI)#or pb.DIRECT for non-graphical version
pb.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally
pb.setGravity(0,0,-10)

planeId = pb.loadURDF("plane.urdf")

startPos = [0,0,1]
startOrientation = pb.getQuaternionFromEuler([0,0,0])

drone_id = pb.loadURDF("drone_simple.urdf",startPos, startOrientation)

force0 = 0.5

#links 7 to 10
for i in range (10000):
	
	if i > 85:
		pb.applyExternalForce(
			drone_id,
			0,
			forceObj=[0, 0, force0],
			posObj=[0, 0, 0],
			flags=pb.LINK_FRAME
		)
		pb.applyExternalForce(
			drone_id,
			1,
			forceObj=[0, 0, force0],
			posObj=[0, 0, 0],
			flags=pb.LINK_FRAME
		)
		pb.applyExternalForce(
			drone_id,
			2,
			forceObj=[0, 0, force0],
			posObj=[0, 0, 0],
			flags=pb.LINK_FRAME
		)
		pb.applyExternalForce(
			drone_id,
			3,
			forceObj=[0, 0, force0],
			posObj=[0, 0, 0],
			flags=pb.LINK_FRAME
		)
	
	if i > 100:
		force0 = 0.067
	
	pb.stepSimulation()
	time.sleep(1./240.)
	
cubePos, cubeOrn = pb.getBasePositionAndOrientation(drone_id)
print(cubePos,cubeOrn)

pb.disconnect()
