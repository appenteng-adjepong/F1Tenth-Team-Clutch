#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32 # Float32 message class
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy, QoSLivelinessPolicy


class MyNode(Node):

    def __init__(self):
        super().__init__("first_node")
        # creata a timer that calls a timer_callback
        self.create_timer(1.0, self.timer_callback)
        self.counter = 0
    def timer_callback(self):
        self.get_logger().info(f"Hello from ROS {self.counter}")
        self.counter+=1

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




def main(args=None):
    rclpy.init(args=args)
    # create node here instance of a function
    new_bridge = rclpy.create_node('new_bridge') # Create ROS 2 node 

    pub_steering_command = new_bridge.create_publisher(Float32, '/steering_command_clutch', qos_profile)
    pub_steering_command
    
    # keep node running until kill command is recieved
    rclpy.spin(new_bridge) # spin actually enables all the callbacks 
    # shutdown node
    rclpy.shutdown()

if __name__=='__main__':
    main()

