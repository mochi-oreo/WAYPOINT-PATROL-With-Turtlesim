cmake_minimum_required(VERSION 3.0.2)
project(turtle_autonomous_mission)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  message_generation
  rospy
  std_msgs
  turtlesim
)

add_message_files(
  FILES
  MissionStatus.msg
)

add_service_files(
  FILES
  StartMission.srv
)

generate_messages(
  DEPENDENCIES
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS geometry_msgs message_runtime rospy std_msgs turtlesim
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)
