import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
 
 
from launch_ros.actions import Node
import xacro
 
 
def generate_launch_description():
 
    # Specify the name of the package and path to xacro file within the package
    pkg_name = 'panda_data'
    file_subpath = 'config/panda.urdf'
    #file_subpath = 'worlds/tpl_with_robot_final.sdf'
 
    # Use xacro to process the file
    xacro_file = os.path.join(get_package_share_directory(pkg_name),file_subpath)
    
    
    rviz_relative_path = 'rviz/config.rviz'

    rviz_absolute_path = os.path.join(xacro_file, rviz_relative_path)
    
    robot_description_raw = xacro.process_file(xacro_file).toxml()
    
    world_path = os.path.join(xacro_file, 'worlds', 'tpl2.world')
 
 
    # Configure the node
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw,
        'use_sim_time': True}] # add other parameters here if required
    )
    
    
    # Rviz2 node
    #node_rviz = Node(
    #    package='rviz2',
    #    executable='rviz2',
    #    name='rviz2',
    #    arguments=['-d', rviz_absolute_path]
    #)
    
    # Configuring Gazebo
    gazebo= ExecuteProcess(
        cmd=['gazebo', '-u', "--verbose",
             "-s", "libgazebo_ros_factory.so",
             "-s", "libgazebo_ros_init.so" 
             ],
        output='screen'
    )
 
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                    arguments=['-topic', 'robot_description',
                                '-entity', 'my_bot'],
                    output='screen')
 
    #  method 1: 
    # spawning the joint broadcaster
    #old
    spawn_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )
    
    spawn_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller"],
        output="screen",
    )

    # method 2:
    # Joint State Broadcaster
    #joint_state_broadcaster = ExecuteProcess(
    #    cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
    #         'joint_state_broadcaster'],
    #    output='screen'
    #)    

    # Joint Trajectory Controller
    #joint_arm_position_controller = ExecuteProcess(
    #    cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
    #         'panda_arm_controller'],
    #    output='screen'
    #)

    # Joint Effort Controller
    #joint_gripper_position_controller = ExecuteProcess(
    #    cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
    #         'hand_controller'],
    #    output='screen'
    #)

    # Run the node
    return LaunchDescription([
    	node_robot_state_publisher,
        gazebo,
        spawn_entity,
        # method 2
        #RegisterEventHandler(
        #    event_handler=OnProcessExit(
        #        target_action=spawn_entity,
        #        on_exit=[joint_state_broadcaster],
        #    )
        #),
        #RegisterEventHandler(
        #    event_handler=OnProcessExit(
        #        target_action=joint_state_broadcaster,
        #        on_exit=[joint_arm_position_controller],
        #    )
        #),        
        #RegisterEventHandler(
        #    event_handler=OnProcessExit(
        #        target_action=joint_state_broadcaster,
        #        on_exit=[joint_gripper_position_controller],
        #    )
        #)
        #node_rviz
        # method 1
        spawn_broadcaster,
        spawn_controller
    ])
 
 
