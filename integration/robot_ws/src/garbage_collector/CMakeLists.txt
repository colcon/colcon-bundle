cmake_minimum_required(VERSION 2.8.3)
project(garbage_collector)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)
# set(OpenCV_DIR /home/ubuntu/build/OpenCV/build)
## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
  cv_bridge
  image_transport
  roscpp
  sensor_msgs
  std_msgs
  tf
  angles
)
## System dependencies are found with CMake's conventions
find_package(OpenCV REQUIRED)

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES blob_tracking_pkg
#  CATKIN_DEPENDS cv_bridge image_transport roscpp sensor_msgs std_msgs
#  DEPENDS system_lib
)

###########
## Build ##
###########

include_directories(
# include
  ${catkin_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
)

add_executable(garbage_collector src/garbage_collector.cpp)
add_dependencies(garbage_collector ${garbage_collector_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

## Specify libraries to link a library or executable target against
target_link_libraries(garbage_collector
  ${catkin_LIBRARIES}
  ${OpenCV_LIBRARIES}
)

## Install scripts
install(TARGETS garbage_collector
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch 
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
