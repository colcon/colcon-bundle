#include "ros/ros.h"
#include "std_msgs/String.h"

#include <sstream>
#include <iostream>
using namespace std;

int main(int argc, char **argv)
{
  ros::init(argc, argv, "helloworld");

  cout << "Hello World! I am a robot!\n";
  
  return 0;
}
