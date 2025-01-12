#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

class MyNode(Node):

    def __init__(self):
        super().__init__("first_node")
        # creata a timer that calls a timer_callback
        self.create_timer(1.0, self.timer_callback)
        self.counter = 0
    def timer_callback(self):
        self.get_logger().info(f"Hello from ROS {self.counter}")
        self.counter+=1


def main(args=None):
    rclpy.init(args=args)
    # create node here instance of a function
    node = MyNode() 
    # keep node running until kill command is recieved
    rclpy.spin(node) # spin actually enables all the callbacks 
    # shutdown node
    rclpy.shutdown()

if __name__=='__main__':
    main()

