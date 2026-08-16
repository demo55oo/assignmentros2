#!/usr/bin/env python3
"""Small slider GUI for commanding all five arm servos."""

import math
import tkinter as tk

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


JOINT_NAMES = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']
JOINT_LABELS = [
    'Base rotation',
    'Shoulder',
    'Elbow',
    'Wrist',
    'Gripper',
]


class ArmCommander(Node):
    def __init__(self):
        super().__init__('arm_commander')
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10,
        )

    def send_degrees(self, servo_degrees):
        message = JointTrajectory()
        message.joint_names = JOINT_NAMES

        point = JointTrajectoryPoint()
        # A physical hobby servo's 90 degrees is the URDF joint's zero angle.
        point.positions = [
            math.radians(float(angle) - 90.0) for angle in servo_degrees
        ]
        point.time_from_start.sec = 2
        message.points = [point]

        self.publisher.publish(message)
        self.get_logger().info(
            'Commanded servo angles: ' +
            ', '.join(f'{angle:.0f}' for angle in servo_degrees)
        )


class CommanderWindow:
    def __init__(self, node):
        self.node = node
        self.root = tk.Tk()
        self.root.title('ROS 2 Robotic Arm Commander')
        self.root.resizable(False, False)
        self.scales = []

        title = tk.Label(
            self.root,
            text='Servo angles (degrees)',
            font=('TkDefaultFont', 12, 'bold'),
        )
        title.grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 8))

        for index, label in enumerate(JOINT_LABELS, start=1):
            tk.Label(self.root, text=label, anchor='w', width=15).grid(
                row=index,
                column=0,
                padx=(12, 4),
                pady=3,
            )
            scale = tk.Scale(
                self.root,
                from_=0,
                to=180,
                orient=tk.HORIZONTAL,
                length=300,
                resolution=1,
            )
            scale.set(90)
            scale.grid(row=index, column=1, padx=(4, 12), pady=3)
            self.scales.append(scale)

        send_button = tk.Button(
            self.root,
            text='Send trajectory',
            command=self.send,
            width=24,
        )
        send_button.grid(
            row=len(JOINT_LABELS) + 1,
            column=0,
            columnspan=2,
            pady=12,
        )
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.after(20, self.spin_ros)

    def send(self):
        self.node.send_degrees([scale.get() for scale in self.scales])

    def spin_ros(self):
        if rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.0)
            self.root.after(20, self.spin_ros)

    def close(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main(args=None):
    rclpy.init(args=args)
    node = ArmCommander()
    try:
        CommanderWindow(node).run()
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
