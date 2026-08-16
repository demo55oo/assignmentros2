from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'arm_assignment'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student',
    maintainer_email='student@example.com',
    description='Five-joint robotic arm simulation and Arduino serial bridge.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'arm_commander = arm_assignment.arm_commander:main',
            'serial_bridge = arm_assignment.serial_bridge:main',
        ],
    },
)
