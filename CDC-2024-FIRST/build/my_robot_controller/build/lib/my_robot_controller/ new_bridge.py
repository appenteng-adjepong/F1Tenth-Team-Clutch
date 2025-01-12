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
sio = socketio.Server(async_mode='gevent',logger=False, engineio_logger=False)   



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

class VehicleCommandNode(Node):

    def __init__(self): #Creat a constructor
        super().__init__("clutch_bridge")
        
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

        self.steering_command_subscriber = self.create_subscription(Float32, '/autodrive_clutch/steering_command', self.callback_steering_command_sub, qos_profile)
        self.throttle_command_subscriber = self.create_subscription(Float32, '/autodrive_clutch/throttle_command', self.callback_throttle_command_sub, qos_profile)

        self.get_logger().info(f"Bridge Node Initiated")

        # Parameters
        self.DRIVE_STEP_SIZE = 1e-4
        self.STEER_STEP_SIZE = 1
        self.steering = 0
        self.throttle = 0.008
        self.counter = 0


   
   

    # VEHICLE DATA SUBSCRIBER CALLBACKS
    def callback_throttle_command_sub(self, throttle_command_msg):
        global throttle_command
        throttle_command = float(np.round(throttle_command_msg.data, 3))

    def callback_steering_command_sub(self, steering_command_msg):
        global steering_command
        steering_command = float(np.round(steering_command_msg.data, 3))

    def timer_callback(self):
        self.get_logger().info(f"Call {self.counter}")
        self.counter+=1
        # Publish control messages




def main(args=None):
    rclpy.init(args=args)
    # create node here instance of a function
    # new_bridge = rclpy.create_node('new_bridge') # Create ROS 2 node 
    # pub_steering_command = new_bridge.create_publisher(Float32, '/autodrive_clutch/steering_command', qos_profile)
    # pub_throttle_command = new_bridge.create_publisher(Float32, '/autodrive_clutch/throttle_command', qos_profile)
    # sub_steering_command = new_bridge.create_subscription(Float32, '/autodrive_clutch/steering_command', callback_throttle_command, qos_profile)
    # sub_throttle_command = new_bridge.create_subscription(Float32, '/autodrive_clutch/throttle_command', callback_steering_command, qos_profile)
    new_bridge = VehicleCommandNode() 

    print("Starting web service")
    app = socketio.WSGIApp(sio) # Create socketio WSGI application
    pywsgi.WSGIServer(('', 4567), app, handler_class=WebSocketHandler).serve_forever() # Deploy as a gevent WSGI server
    
    executor = rclpy.executors.SingleThreadedExecutor() # Create executor to control which threads callbacks get executed in
    executor.add_node(new_bridge) # Add node whose callbacks should be managed by this executor

    # process = Thread(target=executor.spin, daemon=True) # Runs callbacks in the thread
    # process.start() # Activate the thread as demon (background process) and prompt it to the target function (spin the executor)

    # keep node running until kill command is recieved
    rclpy.spin(new_bridge) # spin actually enables all the callbacks 

    # shutdown node
    rclpy.shutdown()

if __name__=='__main__':
    main()




