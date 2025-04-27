from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    tracking_viz = Node(
        package='tracking_visualization',
        executable='tracking_visualization',
        name='robot_trajectory_visualization',
        parameters=[
            {"frame_id": "odom"},
            {"movement_threashold": 0.05},
            {"max_poses": 500},
        ],
        # namespace='visualization',
        output='both',
        emulate_tty=True,
        remappings=[
            (
                'odom_topic',
                '/odometry/filtered',
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
                'robot_odom_tracking.rviz',
            )
        ],
    )

    return LaunchDescription([tracking_viz, rviz])
