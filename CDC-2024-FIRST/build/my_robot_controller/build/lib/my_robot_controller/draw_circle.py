#!/usr/bin/env python3

import rclpy
from rclpy.node import Node   
from rclpy.qos import QoSProfile # Ouality of Service (tune communication between nodes)


#to obtain the message type:  $ topic info /turtle1/cmd_vel   -->  Type: geometry_msgs/msg/Twist
from geometry_msgs.msg import Twist   # make sure you add this dependency in the package.xml file


class DrawCircleNode(Node):

    def __init__(self): #Creat a constructor
        super().__init__("draw_circle")
        qos = QoSProfile(depth=1)
        # self.cmd_vel_pub_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10) # 10 is buffer size or queue size or num msgs
        self.cmd_vel_pub_ = self.create_publisher(Twist, "/turtle1/cmd_vel", qos) # 10 is buffer size or queue size or num msgs
        self.timer_ = self.create_timer(0.5, self.send_velocity_command)
        self.get_logger().info(f"Draw circle node has been initialized")

    def send_velocity_command(self):
        # ros2 interface show geometry_msgs/mgeometry_msgs/msg/Twist
        msg = Twist()
        msg.linear.x =  2.0
        msg.angular.z = 1.0
        self.cmd_vel_pub_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    # create node here instance of a function
    node = DrawCircleNode() 
    # keep node running until kill command is recieved
    rclpy.spin(node) # spin actually enables all the callbacks 
    # shutdown node
    rclpy.shutdown()
