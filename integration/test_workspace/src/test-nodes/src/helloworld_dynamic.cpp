#include "ros/ros.h"
#include "std_msgs/String.h"
#include <ecl/math.hpp>
#include <aws/core/Version.h>
#include <iostream>
using namespace std;

/**
 * This tutorial demonstrates simple sending of messages over the ROS system.
 */

using ecl::pi;

int main(int argc, char **argv)
{
  /**
   * The ros::init() function needs to see argc and argv so that it can perform
   * any ROS arguments and name remapping that were provided at the command line.
   * For programmatic remappings you can use a different version of init() which takes
   * remappings directly, but for most command-line programs, passing argc and argv is
   * the easiest way to do it.  The third argument to init() is the name of the node.
   *
   * You must call one of the versions of ros::init() before using any other
   * part of the ROS system.
   */
  ros::init(argc, argv, "helloworld");

  ecl::isApprox(3.0,3.0000000000000001);

  cout << "Hello World!\n";
  cout << "Test test-nodes passed...\n";


  return 0;
}
