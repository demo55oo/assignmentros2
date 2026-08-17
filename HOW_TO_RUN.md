# How to test & record — Robotic arm (Lab / assignmentros2)

Full **operational** guide: build, run simulation, what each terminal should show, hardware path, and recording tips.  
For URDF / controllers / bridge internals, see [`TECHNICAL.md`](TECHNICAL.md).

Repo: https://github.com/demo55oo/assignmentros2

**Demo video:** https://www.loom.com/share/1761c3ae3028425488cb573162f93b29

---

## What this assignment proves

**Part 1 — Simulation:** a five-joint arm (base, shoulder, elbow, wrist, gripper) with correct dimensions, running in Gazebo + RViz under `ros2_control`, commanded by a slider GUI that publishes `JointTrajectory`.

**Part 2 — Hardware:** the same trajectory topic is converted to five servo angles and sent over USB serial to an Arduino that drives the servos.

**Environment:** Ubuntu 24.04 (WSL2) + ROS 2 Jazzy + Gazebo Harmonic. Arduino IDE on the machine that flashes the board.

---

## One-time setup

```bash
sudo apt update
sudo apt install \
  python3-colcon-common-extensions python3-rosdep python3-serial python3-tk \
  ros-jazzy-controller-manager ros-jazzy-gz-ros2-control \
  ros-jazzy-joint-state-broadcaster \
  ros-jazzy-joint-trajectory-controller \
  ros-jazzy-ros-gz ros-jazzy-robot-state-publisher \
  ros-jazzy-rviz2 ros-jazzy-xacro

mkdir -p ~/arm_ws/src
cp -r /mnt/c/Users/Adham/Documents/course/assignmentros2/arm_assignment ~/arm_ws/src/
cd ~/arm_ws
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Validate the model once:

```bash
cd ~/arm_ws
xacro src/arm_assignment/urdf/robot_arm.urdf.xacro > /tmp/robot_arm.urdf
check_urdf /tmp/robot_arm.urdf
```

**Expect:** `check_urdf` finishes without errors (links/joints graph OK).

After every new terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/arm_ws/install/setup.bash
```

---

## Part 1 — Simulation terminals

### Terminal 1 — Gazebo + RViz + controllers

```bash
cd ~/arm_ws
source install/setup.bash
ros2 launch arm_assignment simulation.launch.py
```

**Expect:**

- Gazebo opens with the arm in `arm_world`.
- RViz shows the same robot (if `rviz:=true`, default).
- Controllers spawn: `joint_state_broadcaster` and `arm_controller` become **active**.

If the view is cropped: click the 3D view → scroll to zoom out → orbit so the full arm is visible.

Quick check in another terminal:

```bash
source ~/arm_ws/install/setup.bash
ros2 control list_controllers
ros2 topic echo /joint_states --once
```

### Terminal 2 — slider commander GUI

```bash
cd ~/arm_ws
source install/setup.bash
ros2 run arm_assignment arm_commander
```

**Expect:** Tk window with five sliders (Base, Shoulder, Elbow, Wrist, Gripper) in **degrees**.  
Move sliders → click **Send trajectory** → arm moves smoothly over ~2 seconds in Gazebo/RViz.

Without GUI (optional smoke test):

```bash
ros2 topic pub --once /arm_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  "{joint_names: [joint1, joint2, joint3, joint4, joint5], points: [{positions: [0.5, -0.4, 0.6, -0.2, 0.3], time_from_start: {sec: 2}}]}"
```

Note: GUI uses **servo degrees** where **90° ≈ URDF zero**. The node converts `radians(deg - 90)` before publishing.

---

## Recording Part 1 (recommended for demo)

1. Enlarge fonts in Terminal 1 / 2.
2. Start **Win + G** screen recording.
3. Show you launching `simulation.launch.py`.
4. Show Gazebo + RViz with the full arm in frame (zoom out).
5. Launch `arm_commander`, move several joints, hit **Send trajectory**.
6. Optionally show `ros2 control list_controllers` with both active.
7. Stop recording; keep a screenshot of the posed arm.

---

## Part 2 — Hardware (when Arduino + servos are ready)

### Flash Arduino

1. Open `arduino/arm_servo_controller/arm_servo_controller.ino` in Arduino IDE.
2. Select board + port → Upload.

**Signal pins:**

| Servo | Joint | Pin |
|-------|-------|-----|
| 1 | Base | D3 |
| 2 | Shoulder | D5 |
| 3 | Elbow | D6 |
| 4 | Wrist | D9 |
| 5 | Gripper | D10 |

Use an **external 5–6 V** supply for servos (not Arduino 5V). Common GND with Arduino.

Linux serial access (once):

```bash
sudo usermod -a -G dialout "$USER"
# then sign out / back in
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

### Terminals for hardware

```bash
# After sourcing ~/arm_ws/install/setup.bash
ros2 launch arm_assignment hardware.launch.py port:=/dev/ttyACM0
```

If the device is USB serial:

```bash
ros2 launch arm_assignment hardware.launch.py port:=/dev/ttyUSB0
```

**Expect:** serial bridge connects; commander GUI (if launched) sends trajectories; physical servos move.  
Line format on serial: `a,b,c,d,e\n` degrees, e.g. `90,45,120,60,0`.

Calibration without code edits:

```bash
ros2 run arm_assignment serial_bridge --ros-args \
  -p port:=/dev/ttyACM0 \
  -p servo_offsets:="[90.0, 92.0, 87.0, 90.0, 80.0]" \
  -p invert:="[false, true, false, false, false]"
```

---

## What “good” looks like

| Check | Pass |
|-------|------|
| `check_urdf` | No errors |
| `ros2 control list_controllers` | `joint_state_broadcaster` + `arm_controller` → `active` |
| Send trajectory | Visible motion in Gazebo/RViz |
| `/joint_states` | Five joints updating |
| Hardware | Serial open; servos track commanded angles |

---

## Common failures

| Symptom | Fix |
|---------|-----|
| Package not found | Rebuild + `source ~/arm_ws/install/setup.bash` |
| Controllers never active | Wait longer; check Gazebo spawned robot; read T1 logs |
| GUI opens but arm static | Controllers not active / wrong topic |
| Serial permission denied | `dialout` group + re-login; correct `/dev/tty*` |
| Servos jitter / weak | External PSU + common ground |

---

## Related docs

- [`TECHNICAL.md`](TECHNICAL.md) — URDF, `ros2_control`, bridge math, file map  
- [`README.md`](README.md) — short overview (original assignment README)
