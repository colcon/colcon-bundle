#include "rclcpp/rclcpp.hpp"
#include <stdio.h>

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  printf("Test cpp package succeeded!!\n");
  rclcpp::shutdown();
  return 0;
}
