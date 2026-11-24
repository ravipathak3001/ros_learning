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
            namespace='robot1'
        ),
        Node(
            package='my_first_package',
            executable='wall_bouncer',
            name='wall_bouncer',
            namespace='robot1',
            parameters=[config],
            output='screen',            # show this nodes log in terminal
        ),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim1',
            namespace='robot2'
        ),
        Node(
            package='my_first_package',
            executable='wall_bouncer',
            name='wall_bouncer',
            namespace='robot2',
            parameters=[{'margin':1.5, 'drive_speed':3.0}],
            output='screen',            # show this nodes log in terminal
        ),
    ])