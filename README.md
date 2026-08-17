# ROS 2 Robotic Arm Assignment

This project contains both assignment parts:

- Part 1: a dimensioned five-joint URDF/Xacro arm, RViz, Gazebo Sim,
  `ros2_control`, and a trajectory-command GUI.
- Part 2: a ROS 2 serial bridge and an Arduino sketch for five servos.

The model uses the dimensions from the assignment: 7.1 cm base, 10 cm L1,
12.8 cm L2, 7 cm L3, and an 11 cm end effector.

## Team
- Adham Mansour Elsaid — 23012143
- Hamza Mohamed Yasser — 21012014
- Aley eldin osama ali Ali 23012080
- mohamed ahmed hesham 23012194
- Youssef abdelkader mohamed 23010144



## Project layout

```text
arm_assignment/
  arm_assignment/
    arm_commander.py       Slider GUI and JointTrajectory publisher
    serial_bridge.py       JointTrajectory-to-USB bridge
  config/controllers.yaml  ros2_control configuration
  launch/
    simulation.launch.py   Gazebo + RViz + controllers
    hardware.launch.py     GUI + serial bridge
  urdf/robot_arm.urdf.xacro
  worlds/arm_world.sdf
arduino/
  arm_servo_controller/arm_servo_controller.ino
```

## Requirements

Use Ubuntu 24.04 with ROS 2 Jazzy and Gazebo Harmonic. In a terminal where
ROS is sourced, install the required packages:

```bash
sudo apt update
sudo apt install \
  python3-colcon-common-extensions python3-rosdep python3-serial python3-tk \
  ros-jazzy-controller-manager ros-jazzy-gz-ros2-control \
  ros-jazzy-joint-state-broadcaster \
  ros-jazzy-joint-trajectory-controller \
  ros-jazzy-ros-gz ros-jazzy-robot-state-publisher \
  ros-jazzy-rviz2 ros-jazzy-xacro
```

## Build

Create a ROS workspace and copy `arm_assignment` into its `src` directory:

```bash
mkdir -p ~/arm_ws/src
cp -r arm_assignment ~/arm_ws/src/
cd ~/arm_ws
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Run the following validation before launching:

```bash
xacro src/arm_assignment/urdf/robot_arm.urdf.xacro > /tmp/robot_arm.urdf
check_urdf /tmp/robot_arm.urdf
```

## Part 1: simulation

Start Gazebo, RViz, the robot, and both controllers:

```bash
cd ~/arm_ws
source install/setup.bash
ros2 launch arm_assignment simulation.launch.py
```

In another sourced terminal, start the command GUI:

```bash
ros2 run arm_assignment arm_commander
```

Move the five sliders and click **Send trajectory**. The node publishes
`trajectory_msgs/msg/JointTrajectory` messages on
`/arm_controller/joint_trajectory`.

The publisher can also be tested without the GUI:

```bash
ros2 topic pub --once /arm_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  "{joint_names: [joint1, joint2, joint3, joint4, joint5], points: [{positions: [0.5, -0.4, 0.6, -0.2, 0.3], time_from_start: {sec: 2}}]}"
```

Useful checks:

```bash
ros2 control list_controllers
ros2 topic echo /joint_states
ros2 topic echo /arm_controller/joint_trajectory
```

Both `joint_state_broadcaster` and `arm_controller` should report `active`.

## Part 2: Arduino

Open `arduino/arm_servo_controller/arm_servo_controller.ino` in the Arduino
IDE, select the board and port, then upload it.

The selected signal pins are:

- Servo 1 (base): D3
- Servo 2 (shoulder): D5
- Servo 3 (elbow): D6
- Servo 4 (wrist): D9
- Servo 5 (gripper): D10

Do not power five servos from the Arduino 5 V pin. Use a suitable external
5–6 V servo supply and connect its ground to Arduino GND. Connect every
servo signal wire to its listed pin.

On Linux, grant serial-port access, then sign out and back in once:

```bash
sudo usermod -a -G dialout "$USER"
```

Find the Arduino port:

```bash
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

Launch the complete hardware pipeline:

```bash
source ~/arm_ws/install/setup.bash
ros2 launch arm_assignment hardware.launch.py port:=/dev/ttyACM0
```

If the board appears as `/dev/ttyUSB0`, use that value instead. The bridge
converts URDF radians to servo degrees, clamps each value to 0–180, and sends:

```text
90,45,120,60,0\n
```

The default URDF zero position maps to 90 degrees on each physical servo.
Mechanical differences can be calibrated without editing code:

```bash
ros2 run arm_assignment serial_bridge --ros-args \
  -p port:=/dev/ttyACM0 \
  -p servo_offsets:="[90.0, 92.0, 87.0, 90.0, 80.0]" \
  -p invert:="[false, true, false, false, false]"
```

## Deliverables covered

- Five revolute joints: base, shoulder, elbow, wrist, and gripper
- Visual, collision, mass, and inertia for every link
- RViz configuration and Gazebo world
- `JointTrajectoryController` on `/arm_controller/joint_trajectory`
- Manual trajectory GUI
- Configurable ROS 2 serial bridge
- Arduino parser and five-servo control sketch
