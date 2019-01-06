#include <iostream>
#include <aws/core/Version.h>
using namespace std;

int main(int argc, char **argv)
{
  cout << "Hello World!\n";

  std::cout << "AWS SDK version: " << Aws::Version::GetVersionString() << std::endl;
  std::cout << "test-cmake passed..." << std::endl;

  return 0;
}
