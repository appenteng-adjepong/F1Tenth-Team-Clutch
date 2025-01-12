#!/usr/bin/env python3

import rclpy
from rclpy.node import Node   
from rclpy.qos import QoSProfile # Ouality of Service (tune communication between nodes)
import numpy as np
from threading import Thread

#to obtain the message type:  $ topic info /turtle1/cmd_vel   -->  Type: geometry_msgs/msg/Twist
from std_msgs.msg import Float32 # Float32 message class


# Python mudule imports
import os # Miscellaneous operating system interfaces
import select # Waiting for I/O completion
import sys # System-specific parameters and functions
if os.name == 'nt':
    import msvcrt # Useful routines from the MS VC++ runtime
else:
    import termios # POSIX style tty control
    import tty # Terminal control functions



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





class VehicleCommandNode(Node):

    def __init__(self): #Creat a constructor
        super().__init__("drive_vehicle2")
        # Parameters
        self.DRIVE_STEP_SIZE = 1e-4
        self.STEER_STEP_SIZE = 1

        # Settings
        self.settings = None
        if os.name != 'nt':
            self.settings = termios.tcgetattr(sys.stdin)


        qos = QoSProfile(depth=1)
        self.throttle_publisher = self.create_publisher(Float32, "/autodrive/f1tenth_1/throttle_command", qos) # 10 is buffer size or queue size or num msgs
        self.steering_publisher = self.create_publisher(Float32, "/autodrive/f1tenth_1/steering_command", qos) # 10 is buffer size or queue size or num msgs
        self.get_logger().info(f"Throttle and Steering Command Initiated")

        self.steering = 0
        self.throttle = 0.008

        self.counter = 0

        self.create_timer(1e-16, self.command_throttle_and_steering_callback)

    def command_throttle_and_steering_callback(self):

        key = self.get_key(self.settings)
        if key == 'z' or key == 'Z':
            self.throttle = np.tanh(self.throttle + self.DRIVE_STEP_SIZE)
        elif key == 's' or key == 'S':
            self.throttle = np.tanh(self.throttle - self.DRIVE_STEP_SIZE)
        elif key == 'q' or key == 'Q':
            self.steering = np.tanh(self.steering + self.STEER_STEP_SIZE)
        elif key == 'd' or key == 'D':
            self.steering = np.tanh(self.steering - self.STEER_STEP_SIZE)
        elif key == 'a' or key == 'A':
            self.steering = 0.0
        elif key == 'e' or key == 'E':
            self.throttle = 0.0
        elif key == 'x' or key == 'X':
            self.throttle = 0.0
            self.steering = 0.0
        else:
            if (key == '\x03'): # CTRL+C
               print("CTRL + C detected")
               self.throttle = 0.0
               self.steering = 0.0
            #    rclpy.shutdown() # Shutdown this context
               self.destroy_node()

        # ros2 interface show geometry_msgs/mgeometry_msgs/msg/Twist
        throttle_msg = Float32()
        steering_msg = Float32()
        # throttle_msg.data =  float(np.tanh(np.random.randn(1))*1e-2)
        # self.throttle += np.tanh(np.random.randn(1))*1e-2
        throttle_msg.data =  float(np.tanh(self.throttle))        
        steering_msg.data =  float(np.tanh(self.steering))

        # Generate control messages
        # throttle_msg.data = float(self.throttle)
        # steering_msg.data = float(self.steering)

        # Publish control messages
        self.throttle_publisher.publish(throttle_msg)
        self.steering_publisher.publish(steering_msg)
        
        self.get_logger().info(f"Throttle Command: {throttle_msg.data} \n ,\
                                 Steering Command: {steering_msg.data} \n ,\
                                 Counter: {self.counter}   ")

    # Get keyboard key
    def get_key(self, settings):
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



def main(args=None):

    rclpy.init(args=args)
    # create node here instance of a function
    command_node = VehicleCommandNode() 

    executor = rclpy.executors.SingleThreadedExecutor() # Create executor to control which threads callbacks get executed in
    executor.add_node(command_node) # Add node whose callbacks should be managed by this executor

    # process = Thread(target=executor.spin, daemon=True) # Runs callbacks in the thread
    # process.start() # Activate the thread as demon (background process) and prompt it to the target function (spin the executor)
    # keep node running until kill command is recieved
    
    rclpy.spin(command_node, executor) # spin actually enables all the callbacks 

    command_node.destroy_node() # Explicitly destroy the node
    rclpy.shutdown() # Shutdown this context


if __name__ == '__main__':
    main()


