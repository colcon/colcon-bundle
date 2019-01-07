#include "ros/ros.h"
#include "std_msgs/String.h"
#include <ecl/math.hpp>
#include <aws/core/Version.h>
#include <iostream>
using namespace std;

using ecl::pi;

int main(int argc, char **argv)
{
  ros::init(argc, argv, "helloworld");

  ecl::isApprox(3.0,3.0000000000000001);

  cout << "Hello World!\n";
  cout << "Test test-nodes passed...\n";

  return 0;
}
