from launch import LaunchDescription
from launch_ros.actions import Node

# from launch.actions import IncludeLaunchDescription
# from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    # mocap_qualisys = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         [
    #             FindPackageShare('mocap_qualisys'),
    #             '/launch/qualisys.launch.py',
    #         ]
    #     )
    # )

    mocap_viz = Node(
        package='tracking_visualization',
        executable='tracking_visualization',
        name='robot_trajectory_visualization',
        # namespace='visualization',
        output='both',
        emulate_tty=True,
        remappings=[
            (
                'odom_topic',
                '/ground_truth/odometry',
            ),
        ],
    )

    tracking_viz = Node(
        package='tracking_visualization',
        executable='tracking_visualization',
        name='robot_trajectory_visualization',
        # namespace='visualization',
        output='both',
        emulate_tty=True,
        remappings=[
            (
                'pose_stamped_topic',
                '/mavros/local_position/pose',
            ),
        ],
    )

    rviz = Node(
        package='rviz2',
        namespace='',
        executable='rviz2',
        name='rviz2',
        arguments=[
            '-d'
            + os.path.join(
                get_package_share_directory('tracking_visualization'),
                'rviz',
                'uav_tracking.rviz',
            )
        ],
    )

    return LaunchDescription([mocap_viz, tracking_viz, rviz])
    # return LaunchDescription([mocap_qualisys, mocap_viz, tracking_viz, rviz])
