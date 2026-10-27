# TurtleBot3 + Nav2 autonomous navigation in a custom Gazebo world

**Demo video:** [Watch on Google Drive](https://drive.google.com/file/d/1Dsywo7V6zLqBlb3-BRWh4W5r64kanRJs/view?usp=sharing) (1 min 51 s screen recording, sped up 1.5x)

[![demo](https://github.com/shreyas02005-sudo/tb3_nav2_demo/raw/main/media/demo.gif)](https://github.com/shreyas02005-sudo/tb3_nav2_demo/blob/main/media/demo.gif)

[![Gazebo and RViz](https://github.com/shreyas02005-sudo/tb3_nav2_demo/raw/main/media/screenshot.png)](https://github.com/shreyas02005-sudo/tb3_nav2_demo/blob/main/media/screenshot.png)

A TurtleBot3 Waffle that navigates on its own through a three room house I built in Gazebo, using the standard ROS 2 Nav2 stack. The robot localizes on a saved map, plans a path to a goal you give it, and drives around the obstacles on the way. Nav2 runs with the default TurtleBot3 parameters (AMCL, NavFn planner, DWB controller). I did not write a custom planner or controller.

## Tested environment

- Ubuntu 22.04 (WSL2), ROS 2 Humble, Gazebo Classic 11.10.2
- TurtleBot3 model: waffle, DDS: CycloneDDS
- Gazebo Classic is end of life, but it is the combination the official TurtleBot3 and Nav2 tutorials target, so I chose it for reliability.

## Install

```
sudo apt install ros-humble-desktop ros-humble-gazebo-ros-pkgs ros-humble-navigation2 \
  ros-humble-nav2-bringup ros-humble-turtlebot3 ros-humble-turtlebot3-gazebo \
  ros-humble-turtlebot3-navigation2 ros-humble-rmw-cyclonedds-cpp \
  python3-colcon-common-extensions
```

Cartographer is not needed to run the demo. I only used it to build the map, and the finished map is already in `maps/`.

## Build and run

Clone the repository into a ROS 2 workspace:

```
mkdir -p ~/nav_ws/src && cd ~/nav_ws/src
git clone https://github.com/shreyas02005-sudo/tb3_nav2_demo.git
```

Build and source:

```
cd ~/nav_ws && colcon build && source install/setup.bash
```

Set the environment variables and launch:

```
export TURTLEBOT3_MODEL=waffle
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ros2 launch tb3_nav2_demo demo.launch.py
```

This one command starts Gazebo with the custom world, the robot, Nav2 and RViz. The initial pose is published automatically roughly 30 seconds after launch, which is about when Nav2 is up. After that, click **Nav2 Goal** in RViz and pick a spot on the map. If the laser scan does not line up with the walls, use **2D Pose Estimate** to correct it. To turn off the automatic pose, add `set_initial_pose:=false`.

You can also send a goal from the command line:

```
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: -2.9, y: 4.2}, orientation: {w: 1.0}}}}"
```

## WSL2 tip (optional)

If you run this in WSL2 with an NVIDIA GPU, these variables turn on hardware rendering:

```
export GALLIUM_DRIVER=d3d12
export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
```

## What's in the repo

- `launch/demo.launch.py` - starts everything
- `worlds/my_world.world` - the custom world
- `maps/my_world.pgm`, `maps/my_world.yaml` - the navigation map
- `models/` - Gazebo models used by the world (cafe_table, euro_pallet, suv)

## How I built it

**World.** I made the three room house in the Gazebo Building Editor and added a few models (a cafe table, a pallet and an SUV) as obstacles. The rooms and doorways are fairly narrow, which makes it a decent test for localization and path planning.

**Map.** I drove the robot around with teleop and built the first map with Cartographer. Teleop was unstable at times, so the generated map had drift and some bad spots. I cleaned the `.pgm` by hand on gimp and checked it against the live laser scan in RViz until the scan lined up with the walls. A clean map mattered a lot, because AMCL localization get unreliable if there is a layout mismatch.

**Launch file.** `demo.launch.py` starts Gazebo, spawns the robot, brings up Nav2 and RViz, and sets the initial pose for AMCL, so you can send a goal without any manual setup.

## Messages you may see

These show up in the terminal but do not affect navigation:

- RViz reports that the `nav2_rviz_plugins/Selector` and `Docking` panels failed to load. They come from the stock TurtleBot3 RViz config.
- The global costmap says it is waiting for the `map` frame until the initial pose is set.
- Some red errors appear on Ctrl+C while Nav2 shuts down.
