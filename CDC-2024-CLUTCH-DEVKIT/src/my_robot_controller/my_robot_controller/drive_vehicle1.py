#!/usr/bin/env python3


import rclpy
from rclpy.node import Node   
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy, QoSLivelinessPolicy

import numpy as np
import time
from threading import Thread

# Python mudule imports
import os # Miscellaneous operating system interfaces
import select # Waiting for I/O completion
import sys # System-specific parameters and functions
if os.name == 'nt':
    import msvcrt # Useful routines from the MS VC++ runtime
else:
    import termios # POSIX style tty control
    import tty # Terminal control functions

#to obtain the message type:  $ topic info /turtle1/cmd_vel   -->  Type: geometry_msgs/msg/Twist
from geometry_msgs.msg import Twist   # make sure you add this dependency in the package.xml file
from std_msgs.msg import Float32 # Float32 message class
############################################################################################################################################################



# Parameters
DRIVE_LIMIT = 1.0
STEER_LIMIT = 1.0
DRIVE_STEP_SIZE = 1e-4
STEER_STEP_SIZE = 0.2

# Information
info = """
---------------------------------------
AutoDRIVE - F1TENTH Teleoperation Panel
---------------------------------------

              Q   W   E
              A   S   D
                  X

W/S : Increase/decrease drive command
D/A : Increase/decrease steer command
Q   : Zero steer
E   : Emergency brake
X   : Force stop and reset

Press CTRL+C to quit

NOTE: Press keys within this terminal
---------------------------------------
"""

# Error
error = """
ERROR: Communication failed!
"""

# Get keyboard key
def get_key(settings):
    if os.name == 'nt':
        return msvcrt.getch().decode('utf-8')
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


################################################################################

qos_profile = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,       # Ensure message delivery
    history=QoSHistoryPolicy.KEEP_LAST,              # Only keep the latest message
    depth=1,                                         # Queue size of 1 for minimal latency
    durability=QoSDurabilityPolicy.VOLATILE,         # Do not retain messages if no subscriber is present
    deadline=rclpy.duration.Duration(seconds=1e-4),   # Short deadline for real-time control
    liveliness=QoSLivelinessPolicy.AUTOMATIC         # Automatic publisher liveliness
)

################################################################################





def main():
    # Settings
    settings = None
    if os.name != 'nt':
        settings = termios.tcgetattr(sys.stdin)

    # ROS 2 infrastructure
    rclpy.init()
    # qos_profile = QoSProfile( # Ouality of Service profile
    #     reliability=QoSReliabilityPolicy.RELIABLE, # Reliable (not best effort) communication
    #     history=QoSHistoryPolicy.KEEP_LAST, # Keep/store only up to last N samples
    #     depth=1 # Queue (buffer) size/depth (only honored if the “history” policy was set to “keep last”)
    #     )    
    node = rclpy.create_node('drive_vehicle1')
    pub_steering_command = node.create_publisher(Float32, '/autodrive/f1tenth_1/steering_command', qos_profile)
    pub_throttle_command = node.create_publisher(Float32, '/autodrive/f1tenth_1/throttle_command', qos_profile)

    # Initialize
    throttle_msg = Float32()
    steering_msg = Float32()
    throttle = 0.008
    steering = 0.0


    # executor = rclpy.executors.SingleThreadedExecutor() # Create executor to control which threads callbacks get executed in
    # executor.add_node(node) # Add node whose callbacks should be managed by this executor

    # process = Thread(target=executor.spin, daemon=True) # Runs callbacks in the thread
    # process.start() # Activate the thread as demon (background process) and prompt it to the target function (spin the executor)


    try:
 

        # Generate control commands
        while(1):
            key = get_key(settings)
            if key == 'z' or key == 'Z':
                throttle = np.tanh(throttle + DRIVE_STEP_SIZE)
            elif key == 's' or key == 'S':
                throttle = np.tanh(throttle - DRIVE_STEP_SIZE)
            elif key == 'q' or key == 'Q':
                steering = np.tanh(steering + STEER_STEP_SIZE)
            elif key == 'd' or key == 'D':
                steering = np.tanh(steering - STEER_STEP_SIZE)
            elif key == 'a' or key == 'A':
                steering = 0.0
            elif key == 'e' or key == 'E':
                throttle = 0.0
            elif key == 'x' or key == 'X':
                throttle = 0.0
                steering = 0.0
            else:
                if (key == '\x03'): # CTRL+C
                    break
            
            # Generate control messages
            throttle_msg.data = float(throttle)
            steering_msg.data = float(steering)

            # Publish control messages
            pub_throttle_command.publish(throttle_msg)
            pub_steering_command.publish(steering_msg)


            node.get_logger().info(f"Throttle Command: {throttle_msg.data}")
            node.get_logger().info(f"Steering Command: {steering_msg.data}")

    except Exception as error:
        # Print error
        print(error)

    finally:
        # Generate and publish zero commands
        throttle_msg.data = float(0.0)
        steering_msg.data = float(0.0)
        pub_throttle_command.publish(throttle_msg)
        pub_steering_command.publish(steering_msg)
        if os.name != 'nt':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

