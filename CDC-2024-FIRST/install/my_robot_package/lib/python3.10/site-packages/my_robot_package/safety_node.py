#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

import numpy as np
from sensor_msgs.msg import LaserScan

from std_msgs.msg import Float32

from scipy.signal import butter, lfilter
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy, QoSLivelinessPolicy



class SafetyNode(Node):
    """
    The class that handles emergency braking.
    """
    def __init__(self):
        super().__init__('safety_node')

        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,       # Ensure message delivery
            history=QoSHistoryPolicy.KEEP_LAST,              # Only keep the latest message
            depth=1,                                         # Queue size of 1 for minimal latency
            durability=QoSDurabilityPolicy.VOLATILE,         # Do not retain messages if no subscriber is present
            deadline=rclpy.duration.Duration(seconds=1e-4),  # Short deadline for real-time control
            liveliness=QoSLivelinessPolicy.AUTOMATIC         # Automatic publisher liveliness
        )

        lidarscan_topic = '/autodrive/f1tenth_1/lidar'
        steer_topic = '/autodrive/f1tenth_1/steering_command'
        throttle_topic = '/autodrive/f1tenth_1/throttle_command'

        self.lidar_scanner = self.create_subscription(LaserScan, lidarscan_topic, self.scan_callback, 1)
        self.steering_publisher = self.create_publisher(Float32, steer_topic, 1)
        self.throttle_publisher = self.create_publisher(Float32, throttle_topic, 1)

        self.throttle_msg = Float32()
        self.steering_msg = Float32()
        self.previous_range = np.zeros(1081)
        self.previous_time = 0
        self.ttc_threshold = 10
        

        


    def scan_callback(self, scan_msg):
        # TODO: calculate TTC
        current_time = scan_msg.header.stamp.sec + (scan_msg.header.stamp.nanosec)/1e9
        lidar_array = scan_msg.ranges
        lidar_array = np.where(np.isinf(lidar_array), 10, lidar_array)  # Replace inf with 10
        lidar_array= np.where(np.isnan(lidar_array), 0.06, lidar_array)
        difference = lidar_array-self.previous_range
        dt = current_time-self.previous_time
        self.previous_time = current_time
        self.previous_range=lidar_array
        negated_rate = -1*(difference)/dt
        #print(negated_rate)
        new_rate = np.maximum(negated_rate, 0)
        epsilon = 1e-15  # Small value to prevent division by zero
        ttc = np.where(new_rate > epsilon, lidar_array / new_rate, float('inf'))
        values = np.arange(130, 151)  # Generates values from 130 to 150 (inclusive)
        a = np.round(values * 1080 / 270).astype(int)  # Perform the operation for each value in the array
        print(ttc[a])

        if np.any(ttc < self.ttc_threshold):
            throttle_command =0
        else:
            throttle_command = 0.8
        print(throttle_command)
        self.throttle_msg.data = float(throttle_command)
        self.throttle_publisher.publish(self.throttle_msg)

        
        
        # TODO: publish command to brake
        pass

def main(args=None):
    rclpy.init(args=args)
    print("Emergency Braking Initialized")
    safety_node = SafetyNode()
    rclpy.spin(safety_node)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    safety_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()