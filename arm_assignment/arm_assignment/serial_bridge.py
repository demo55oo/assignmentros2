#!/usr/bin/env python3
"""Bridge ROS 2 joint trajectories to five Arduino servo angles."""

import math

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory

try:
    import serial
except ImportError:
    serial = None


JOINT_NAMES = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']


class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baud', 115200)
        self.declare_parameter('servo_offsets', [90.0] * 5)
        self.declare_parameter('invert', [False] * 5)

        self.connection = None
        self.last_angles = [90] * 5
        self.create_subscription(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            self.trajectory_callback,
            10,
        )
        self.create_timer(2.0, self.connect)
        self.connect()

    def connect(self):
        if self.connection is not None and self.connection.is_open:
            return
        if serial is None:
            self.get_logger().error(
                'pyserial is not installed. Run: sudo apt install python3-serial',
                once=True,
            )
            return

        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value
        try:
            self.connection = serial.Serial(
                port=port,
                baudrate=baud,
                timeout=1.0,
                write_timeout=1.0,
            )
            self.get_logger().info(f'Connected to Arduino on {port} at {baud} baud')
        except serial.SerialException as error:
            self.connection = None
            self.get_logger().warning(
                f'Waiting for Arduino on {port}: {error}',
                throttle_duration_sec=10.0,
            )

    def trajectory_callback(self, message):
        if not message.points:
            self.get_logger().warning('Ignoring trajectory with no points')
            return

        point = message.points[-1]
        if len(point.positions) != len(message.joint_names):
            self.get_logger().warning(
                'Ignoring trajectory: joint_names and positions sizes differ'
            )
            return

        positions = dict(zip(message.joint_names, point.positions))
        offsets = self.get_parameter('servo_offsets').value
        invert = self.get_parameter('invert').value
        if len(offsets) != 5 or len(invert) != 5:
            self.get_logger().error(
                'servo_offsets and invert parameters must each have five values'
            )
            return

        angles = self.last_angles.copy()
        for index, joint_name in enumerate(JOINT_NAMES):
            if joint_name not in positions:
                continue
            degrees = math.degrees(positions[joint_name])
            if invert[index]:
                degrees = -degrees
            angles[index] = round(max(0.0, min(180.0, degrees + offsets[index])))

        self.last_angles = angles
        payload = ','.join(str(angle) for angle in angles) + '\n'
        self.send(payload)

    def send(self, payload):
        if self.connection is None or not self.connection.is_open:
            self.get_logger().warning('Trajectory received, but Arduino is disconnected')
            self.connect()
            return
        try:
            self.connection.write(payload.encode('ascii'))
            self.connection.flush()
            self.get_logger().info(f'Sent: {payload.strip()}')
        except (serial.SerialException, serial.SerialTimeoutException) as error:
            self.get_logger().error(f'Serial write failed: {error}')
            self.connection.close()
            self.connection = None

    def destroy_node(self):
        if self.connection is not None and self.connection.is_open:
            self.connection.close()
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
