#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy, QoSLivelinessPolicy

from threading import Thread

# Python mudule imports
from gevent import pywsgi # Pure-Python gevent-friendly WSGI server
from geventwebsocket.handler import WebSocketHandler # Handler for WebSocket messages and lifecycle events
import socketio # Socket.IO realtime client and server
import numpy as np # Scientific computing

#to obtain the message type:  $ ros2 topic info /turtle1/cmd_vel   -->  Type: geometry_msgs/msg/Twist
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



################################################################################

# # Global declarations
global throttle_command, steering_command

# Initialize vehicle control commands
throttle_command = 0.
steering_command = 0.

#########################################################
# WEBSOCKET SERVER INFRASTRUCTURE
#########################################################

# Initialize the server
sio = socketio.Server(async_mode='gevent')

# Registering "connect" event handler for the server
@sio.on('connect')
def connect(sid, environ):
    print("Connected!")

# Registering "Bridge" event handler for the server
@sio.on('Bridge')
def bridge(sid, data):
    # Global declarations
    global throttle_command, steering_command

    # Vehicle and traffic light control commands
    sio.emit('Bridge', data={'V1 Throttle': str(throttle_command), 'V1 Steering': str(steering_command)})


###########################################################################################################################

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
        super().__init__("my_subscriber_node")
        
        # Settings
        self.settings = None
        if os.name != 'nt':
            self.settings = termios.tcgetattr(sys.stdin)


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

        self.steering_command_publisher = self.create_publisher(Float32, '/autodrive/f1tenth_1/steering_command', qos_profile)
        self.throttle_command_publisher = self.create_publisher(Float32, '/autodrive/f1tenth_1/throttle_command', qos_profile)
        self.lidar_subscriber = self.create_subscription(Float32, '/autodrive/f1tenth_1/lidar', self.callback_lidar_sub, qos_profile)
        #self.throttle_command_subscriber = self.create_subscription(Float32, '/autodrive_clutch/throttle_command', self.callback_throttle_command_sub, qos_profile)
        self.create_timer(1e-6, self.timer_callback)


        self.get_logger().info(f"Node Initiated")

        # Parameters
        self.DRIVE_STEP_SIZE = 1e-3
        self.STEER_STEP_SIZE = .2
        self.steering = 0.
        self.throttle = 0.008
        self.counter = 0.
        # ros2 interface show geometry_msgs/mgeometry_msgs/msg/Twist
        self.throttle_msg = Float32()
        self.steering_msg = Float32()

    def command_throttle_and_steering_callback(self):

        key = self.get_key(self.settings)
        
        # Forward (up arrow or 'z'/'Z')
        if key == '^[[A' or key == 'w' or key == 'W':
            self.throttle = np.tanh(self.throttle + self.DRIVE_STEP_SIZE)
        
        # Backward (down arrow or 's'/'S')
        elif key == '^[[B' or key == 's' or key == 'S':
            self.throttle = np.tanh(self.throttle - self.DRIVE_STEP_SIZE)
        
        # Left (left arrow or 'q'/'Q')
        elif key == '^[[D' or key == 'a' or key == 'A':
            self.steering = np.tanh(self.steering + self.STEER_STEP_SIZE)
        
        # Right (right arrow or 'd'/'D')
        elif key == '^[[C' or key == 'd' or key == 'D':
            self.steering = np.tanh(self.steering - self.STEER_STEP_SIZE)
        
        # Center steering ('a'/'A')
        elif key == 'a' or key == 'A':
            self.steering = 0.0
        
        # Stop throttle ('e'/'E')
        elif key == 'e' or key == 'E':
            self.throttle = 0.0
        
        # Reset throttle and steering ('x'/'X')
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


        # Generate control messages
        self.throttle_msg.data =  float(np.clip(self.throttle, a_min=-1, a_max=1))        
        self.steering_msg.data =  float(np.clip(self.steering, a_min=-1, a_max=1))

        self.throttle_command_publisher.publish(self.throttle_msg)
        self.steering_command_publisher.publish(self.steering_msg)

              
        self.get_logger().info(f"\n,\
                                 Throttle cmd: {self.throttle_msg.data} \n ,\
                                 Steering cmd: {self.steering_msg.data} \n ,\
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



    # VEHICLE DATA SUBSCRIBER CALLBACKS
    def callback_throttle_command_sub(self, throttle_command_msg):
        global throttle_command
        throttle_command = float(np.round(throttle_command_msg.data, 3))

    def callback_steering_command_sub(self, steering_command_msg):
        global steering_command
        steering_command = float(np.round(steering_command_msg.data, 3))

    def timer_callback(self):
        self.command_throttle_and_steering_callback()
        # Publish control messages
        self.throttle_command_publisher.publish(self.throttle_msg)
        self.steering_command_publisher.publish(self.steering_msg)
        # self.get_logger().info(f"Call {self.counter}")
        # self.counter+=1



def main(args=None):
    rclpy.init(args=args)
    # create node here instance of a function
    # new_bridge = rclpy.create_node('new_bridge') # Create ROS 2 node 
    # pub_steering_command = new_bridge.create_publisher(Float32, '/autodrive_clutch/steering_command', qos_profile)
    # pub_throttle_command = new_bridge.create_publisher(Float32, '/autodrive_clutch/throttle_command', qos_profile)
    # sub_steering_command = new_bridge.create_subscription(Float32, '/autodrive_clutch/steering_command', callback_throttle_command, qos_profile)
    # sub_throttle_command = new_bridge.create_subscription(Float32, '/autodrive_clutch/throttle_command', callback_steering_command, qos_profile)
    new_bridge = VehicleCommandNode() 


    # print("Executing node")
    # executor = rclpy.executors.SingleThreadedExecutor() # Create executor to control which threads callbacks get executed in
    # executor.add_node(new_bridge) # Add node whose callbacks should be managed by this executor

    # process = Thread(target=executor.spin, daemon=False) # Runs callbacks in the thread
    # process.start() # Activate the thread as demon (background process) and prompt it to the target function (spin the executor)

    # keep node running until kill command is recieved
    rclpy.spin(new_bridge) # spin actually enables all the callbacks 

    #print("Starting web service")
    #app = socketio.WSGIApp(sio) # Create socketio WSGI application
    #pywsgi.WSGIServer(('', 4567), app, handler_class=WebSocketHandler).serve_forever() # Deploy as a gevent WSGI server
    
    # shutdown node
    rclpy.shutdown()

if __name__=='__main__':
    main()




