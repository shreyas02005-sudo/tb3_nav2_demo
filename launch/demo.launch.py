import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess,
                            IncludeLaunchDescription, TimerAction)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg = get_package_share_directory('tb3_nav2_demo')
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    tb3_nav2 = get_package_share_directory('turtlebot3_navigation2')
    gazebo_ros = get_package_share_directory('gazebo_ros')

    # Bundled models visible to Gazebo; default robot model is waffle.
    os.environ['GAZEBO_MODEL_PATH'] = (
        os.path.join(pkg, 'models') + ':' + os.environ.get('GAZEBO_MODEL_PATH', ''))
    os.environ.setdefault('TURTLEBOT3_MODEL', 'waffle')
    os.environ.setdefault('GAZEBO_MODEL_DATABASE_URI', '')

    world = os.path.join(pkg, 'worlds', 'my_world.world')

    args = [
        DeclareLaunchArgument('map', default_value=os.path.join(pkg, 'maps', 'my_world.yaml')),
        DeclareLaunchArgument('x_pose', default_value='-1.0'),
        DeclareLaunchArgument('y_pose', default_value='-4.0'),
        DeclareLaunchArgument('set_initial_pose', default_value='true'),
    ]

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world}.items())
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros, 'launch', 'gzclient.launch.py')))
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo, 'launch', 'robot_state_publisher.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items())
    spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo, 'launch', 'spawn_turtlebot3.launch.py')),
        launch_arguments={'x_pose': LaunchConfiguration('x_pose'),
                          'y_pose': LaunchConfiguration('y_pose')}.items())

    # Start Nav2 (with RViz) a few seconds after Gazebo is up.
    nav2 = TimerAction(period=10.0, actions=[ExecuteProcess(
        cmd=['ros2', 'launch', 'turtlebot3_navigation2', 'navigation2.launch.py',
             'use_sim_time:=True', ['map:=', LaunchConfiguration('map')]],
        output='screen')])

    # The robot spawns at the map origin (the map was built from this spawn point).
    initial_pose = TimerAction(period=30.0, actions=[ExecuteProcess(
        cmd=['ros2', 'topic', 'pub', '--once', '/initialpose',
             'geometry_msgs/msg/PoseWithCovarianceStamped',
             '{header: {frame_id: map}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, '
             'orientation: {w: 1.0}}, covariance: [0.25,0,0,0,0,0, 0,0.25,0,0,0,0, '
             '0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0.0685]}}'],
        output='screen',
        condition=IfCondition(LaunchConfiguration('set_initial_pose')))])

    return LaunchDescription(args + [gzserver, gzclient, robot_state_publisher,
                                     spawn, nav2, initial_pose])
