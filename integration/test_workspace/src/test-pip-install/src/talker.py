#!/usr/bin/python

import rospy
from geometry_msgs.msg import Vector3

def talker():
	rospy.init_node('talker', anonymous=True)
	pub = rospy.Publisher('cmd_rotate', Vector3, queue_size=1)
	rate = rospy.Rate(2)

	while not rospy.is_shutdown():
		# Rotate 10 degrees around the z axis
		rotation = Vector3(0, 0, 10)

		rospy.loginfo(rotation)

		pub.publish(rotation)

		rate.sleep()

if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		pass
