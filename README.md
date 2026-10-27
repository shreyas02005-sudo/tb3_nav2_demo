# TurtleBot3 + Nav2 autonomous navigation in a custom Gazebo world


**Demo video:** [Watch on Google Drive](https://drive.google.com/file/d/1Dsywo7V6zLqBlb3-BRWh4W5r64kanRJs/view?usp=sharing) (1 min 51 s screen recording, sped up 1.5x)

![demo](media/demo.gif)

![Gazebo and RViz](media/screenshot.png)

This project demonstrates an autonomous navigation pipeline using a TurtleBot3 Waffle configured to navigate a custom three room house environment in Gazebo. It integrates the ROS 2 Navigation2 (Nav2) stack using stock parameter sets, leveraging Cartographer for occupancy grid mapping and manual map refinement to ensure localization stability.

## Tested environment

- Ubuntu 22.04 (WSL2), ROS 2 Humble, Gazebo Classic 11.10.2
- TurtleBot3 model: waffle, DDS: CycloneDDS
- Gazebo Classic is end of life, but it is the combination the official TurtleBot3 and
  Nav2 tutorials target, so I chose it for reliability.

## Install

    sudo apt install ros-humble-desktop ros-humble-gazebo-ros-pkgs ros-humble-navigation2 \
      ros-humble-nav2-bringup ros-humble-turtlebot3 ros-humble-turtlebot3-gazebo \
      ros-humble-turtlebot3-navigation2 ros-humble-rmw-cyclonedds-cpp \
      python3-colcon-common-extensions

## Build and run

Clone the repository into your ROS 2 workspace:

    mkdir -p ~/nav_ws/src && cd ~/nav_ws/src
    git clone https://github.com/shreyas02005-sudo/tb3_nav2_demo.git

Build the workspace and source the environment:

    cd ~/nav_ws && colcon build && source install/setup.bash

Set required environment variables and launch the simulation:

    export TURTLEBOT3_MODEL=waffle
    export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
    ros2 launch tb3_nav2_demo demo.launch.py

One command starts Gazebo (custom world), the robot, Nav2 and RViz. The initial pose is
published automatically about 30 seconds after launch. Then click **Nav2 Goal** in RViz.
If the laser scan does not line up with the walls, use **2D Pose Estimate**.
To disable the automatic pose: `set_initial_pose:=false`.

Command-line goal (To send a navigation goal via the command line):

    ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
      "{pose: {header: {frame_id: map}, pose: {position: {x: -2.9, y: 4.2}, orientation: {w: 1.0}}}}"

## WSL2 tip (optional)

If running inside WSL2 with an NVIDIA GPU, pass these variables to enable hardware rendering acceleration:

    export GALLIUM_DRIVER=d3d12
    export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA

## Contents

- `launch/demo.launch.py` - starts everything
- `worlds/my_world.world` - the custom world
- `maps/my_world.pgm`, `maps/my_world.yaml` - the navigation map
- `models/` - Gazebo models used by the world (cafe_table, euro_pallet, suv)

## Highlights
Custom Environment Design: Designed a multi room residential layout utilizing the Gazebo Building Editor to test localization and path planning performance in confined spaces.

SLAM & Map Iteration: Generated initial occupancy maps via Cartographer SLAM during manual teleoperation. Handled sensor drift and mapping anomalies (such as odometry resets during teleop instability) by manually cleaning and aligning the .pgm costmaps against live laser scan overlays in RViz.

Streamlined Bringup: Engineered a single line launch configuration (demo.launch.py) that synchronizes Gazebo, robot state publishers, Nav2 bringup nodes, and RViz, featuring an automated initial pose publisher to minimize manual setup overhead.


