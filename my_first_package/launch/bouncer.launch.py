import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('my_first_package'), 'config', 'bouncer.yaml'
    )
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim',
        ),
        Node(
            package='my_first_package',
            executable='wall_bouncer',
            name='wall_bouncer',
            parameters=[config],
            output='screen',            # show this nodes log in terminal
        ),
    ])