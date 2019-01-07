cmake_minimum_required(VERSION 2.8.3)
project(test-nodes)

set (CMAKE_CXX_STANDARD 11)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  ecl_math
)

find_package(AWSSDK)

set(AWS_DEPS monitoring)
AWSSDK_DETERMINE_LIBS_TO_LINK(AWS_DEPS AWS_LIBS)
link_directories("${AWSSDK_LIB_DIR}")


catkin_package(
)


include_directories(
  ${catkin_INCLUDE_DIRS}
)

add_executable(helloworld src/helloworld.cpp)
target_link_libraries(helloworld ${catkin_LIBRARIES})

add_executable(helloworld_dynamic src/helloworld_dynamic.cpp)
target_link_libraries(helloworld_dynamic ${catkin_LIBRARIES} ${AWS_LIBS})


## Install scripts
install(TARGETS helloworld helloworld_dynamic
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch)

find_package(catkin REQUIRED COMPONENTS roslaunch)
roslaunch_add_file_check(launch)
