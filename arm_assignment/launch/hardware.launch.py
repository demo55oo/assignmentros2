"""Launch the manual arm commander and Arduino serial bridge."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    port = LaunchConfiguration('port')
    baud = LaunchConfiguration('baud')

    return LaunchDescription([
        DeclareLaunchArgument(
            'port',
            default_value='/dev/ttyACM0',
            description='Arduino serial device',
        ),
        DeclareLaunchArgument(
            'baud',
            default_value='115200',
            description='Arduino serial baud rate',
        ),
        Node(
            package='arm_assignment',
            executable='serial_bridge',
            name='serial_bridge',
            parameters=[{
                'port': port,
                'baud': ParameterValue(baud, value_type=int),
            }],
            output='screen',
        ),
        Node(
            package='arm_assignment',
            executable='arm_commander',
            name='arm_commander',
            output='screen',
        ),
    ])
