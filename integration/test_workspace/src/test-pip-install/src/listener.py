#!/usr/bin/python

import rospy
from geometry_msgs.msg import Vector3
import pyquaternion

class Listener:
	def __init__(self):
		self.quat = [ 1, 0, 0 ]
		rospy.Subscriber("cmd_rotate", Vector3, self.callback)


	def callback(self, data):
		x_rotation = pyquaternion.Quaternion(axis=[1, 0, 0], degrees=data.x)
		y_rotation = pyquaternion.Quaternion(axis=[0, 1, 0], degrees=data.y)
		z_rotation = pyquaternion.Quaternion(axis=[0, 0, 1], degrees=data.z)

		self.quat = x_rotation.rotate(self.quat)
		self.quat = y_rotation.rotate(self.quat)
		self.quat = z_rotation.rotate(self.quat)

		rospy.loginfo(rospy.get_caller_id() + "Rotated vector is %s", str(self.quat))

if __name__ == '__main__':
	rospy.init_node('listener', anonymous=True)
	listener = Listener()
	rospy.spin()

