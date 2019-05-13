cmake_minimum_required (VERSION 2.8.3)
project (hello)
add_executable(hello hello.cpp)
install (TARGETS hello DESTINATION bin)