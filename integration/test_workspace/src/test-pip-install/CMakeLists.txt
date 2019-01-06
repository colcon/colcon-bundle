cmake_minimum_required(VERSION 2.8.3)
project(test-pip-install)

set(CATKIN_DEPS geometry_msgs rospy)

find_package(catkin REQUIRED COMPONENTS ${CATKIN_DEPS})

catkin_package()

catkin_install_python(PROGRAMS src/talker.py src/listener.py src/test-pip-install.py
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})

install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch)

find_package(catkin REQUIRED COMPONENTS roslaunch rospy)
