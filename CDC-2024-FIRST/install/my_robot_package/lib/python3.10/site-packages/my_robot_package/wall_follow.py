# import rclpy
# from rclpy.node import Node

# import numpy as np
# from sensor_msgs.msg import LaserScan

# from std_msgs.msg import Float32

# from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy, QoSLivelinessPolicy

# class WallFollow(Node):
#     """ 
#     Implement Wall Following on the car
#     """
#     def __init__(self):
#         super().__init__('wall_follow_node')

#         qos_profile = QoSProfile(
#             reliability=QoSReliabilityPolicy.RELIABLE,       # Ensure message delivery
#             history=QoSHistoryPolicy.KEEP_LAST,              # Only keep the latest message
#             depth=1,                                         # Queue size of 1 for minimal latency
#             durability=QoSDurabilityPolicy.VOLATILE,         # Do not retain messages if no subscriber is present
#             deadline=rclpy.duration.Duration(seconds=1e-4),   # Short deadline for real-time control
#             liveliness=QoSLivelinessPolicy.AUTOMATIC         # Automatic publisher liveliness
#         )

#         lidarscan_topic = '/autodrive/f1tenth_1/lidar'
#         # drive_topic = '/drive/
#         steer_command = '/autodrive/f1tenth_1/steering_command'
#         throttle_command = '/autodrive/f1tenth_1/throttle_command'

#         # TODO: create subscribers and publishers
#         self.lidar_scanner = self.create_subscription(LaserScan, lidarscan_topic, self.scan_callback,1)
#         self.steering_publisher = self.create_publisher(Float32, steer_command, 1)
#         self.throttle_publisher = self.create_publisher(Float32, throttle_command, 1)

#         self.throttle_msg = Float32()
#         self.steering_msg = Float32()

#         # TODO: set PID gains
#         self.kp = 0.5
#         self.kd = 0
#         self.ki = 0

#         # TODO: store history
#         self.integral = 0
#         self.prev_error = 0 
#         self.error = 0
#         self.differential = 0
        

#         # TODO: store any necessary values you think you'll need

#     def get_range(self, range_data, angle):
#         """
#         Simple helper to return the corresponding range measurement at a given angle. Make sure you take care of NaNs and infs.

#         Args:
#             range_data: single range array from the LiDAR
#             angle: between angle_min and angle_max of the LiDAR

#         Returns:
#             range: range measurement in meters at the given angle

#         """


#         index = int(np.round((angle/270)*1079))

#         #TODO: implement
#         # range_data[np.isnan(range_data)] = 0.06
#         # range_data[np.isinf(range_data)] = 10.0

#         return range_data[index]

#     def get_error(self, range_data, dist):
#         """
#         Calculates the error to the wall. Follow the wall to the left (going counter clockwise in the Levine loop). You potentially will need to use get_range()

#         Args:
#             range_data: single range array from the LiDAR
#             dist: desired distance to the wall

#         Returns:
#             error: calculated error
#         """
#         theta = 45
#         L = 0.1

#         a = self.get_range(range_data, 45)
#         b = self.get_range(range_data, 45 + theta)

#         alpha = np.arctan2(a*np.cos(theta) - b, a*np.sin(theta))
#         Dt = b*np.cos(alpha)

#         Dt1 = Dt + L*np.sin(alpha)

        

#         #TODO:implement
#         return -(Dt1-dist)

#     def pid_control(self, error, velocity):
#         """
#         Based on the calculated error, publish vehicle control

#         Args:
#             error: calculated error
#             velocity: desired velocity

#         Returns:
#             None
#         """
#         # angle = 70
#         # TODO: Use kp, ki & kd to implement a PID controller
#         self.error = error
#         self.integral += error
#         self.differential = error - self.prev_error
#         self.prev_error = error

#         steering_command = self.kp*self.error + self.ki*self.integral + self.kd*self.differential

#         if (np.abs(steering_command) > 0 and np.abs(steering_command) <= 10):
#             throttle_command = velocity
#         elif (np.abs(steering_command) > 10 and np.abs(steering_command) <= 20):
#             throttle_command = velocity - 0.5
#         else:
#             throttle_command = 0.5

#         # TODO: fill in drive message and publish

#         if np.abs(steering_command) > np.pi*(1/3):
#             steering_command = np.pi*(1/3)


#         self.throttle_msg.data = float(throttle_command)
#         self.throttle_publisher.publish(self.throttle_msg)

#         self.steering_msg.data = float(steering_command)
#         self.steering_publisher.publish(self.steering_msg)


        
        

#     def scan_callback(self, msg):
#         """
#         Callback function for LaserScan messages. Calculate the error and publish the drive message in this function.

#         Args:
#             msg: Incoming LaserScan message

#         Returns:
#             None
#         """
#         dist = 0.5
#         error = self.get_error(msg.ranges, dist) # TODO: replace with error calculated by get_error()
#         velocity = 1.5 # TODO: calculate desired car velocity based on error
#         self.pid_control(error, velocity) # TODO: actuate the car with PID


# def main(args=None):
#     rclpy.init(args=args)
#     print("WallFollow Initialized")
#     wall_follow_node = WallFollow()
#     rclpy.spin(wall_follow_node)

#     # Destroy the node explicitly
#     # (optional - otherwise it will be done automatically
#     # when the garbage collector destroys the node object)
#     wall_follow_node.destroy_node()
#     rclpy.shutdown()


# if __name__ == '__main__':
#     main()
import rclpy
from rclpy.node import Node

import numpy as np
from sensor_msgs.msg import LaserScan

from std_msgs.msg import Float32

from scipy.signal import butter, lfilter
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy, QoSLivelinessPolicy

class WallFollow(Node):
    """ 
    Implement Wall Following on the car
    """
    def __init__(self):
        super().__init__('wall_follow_node')

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
        self.previous_time = 0
        self.current_velocity = 0.008 # Store the current velocity
        self.dt = 0
        # PID parameters
        self.kp = 0.5
        self.kd = 0.03
        self.ki = 0.01
        #self.dt = 0.02500000037252903 # Time interval (assumed 5 Hz)

        # Derivative capping
        self.DERIVATIVE_CAP = 1.0

        # Butterworth filter configuration
        self.CUTOFF_FREQ = 1.0  # Hz
        self.FILTER_ORDER = 2
        self.NYQUIST_FREQ = 2 # Nyquist frequency (5 Hz / 2)
        self.b, self.a = butter(self.FILTER_ORDER, self.CUTOFF_FREQ / self.NYQUIST_FREQ, btype='low')

        # State variables
        self.integral = 0.0
        self.prev_error = 0.0
        self.error = 0.0
        self.differential = 0.0
        self.dt1_buffer = []  # Buffer for smoothed distance values

    def butterworth_filter(self, data):
        """Apply the Butterworth filter to the data."""
        return lfilter(self.b, self.a, data)

    def get_range(self, range_data, angle):
        """
        Helper to return the corresponding range measurement at a given angle.
        """
        index = int(np.round((angle / 270) * 1079))
        return range_data[index]

    def get_error(self, range_data, dist):
        """
        Calculates the error to the wall.
        """
        theta = 45  # Angle to the wall
        if self.dt>5:
            self.dt = 0.25
        L = self.current_velocity * self.dt # Distance forward to calculate projected position
        range_data = np.where(np.isinf(range_data), 10, range_data)  # Replace inf with 10
        range_data = np.where(np.isnan(range_data), 0.06, range_data)
        a = self.get_range(range_data, 270-45)
        b = self.get_range(range_data, 270-(45 + theta))

        alpha = np.arctan2(a * np.cos(np.radians(theta)) - b, a * np.sin(np.radians(theta)))
        Dt = b * np.cos(alpha)
        print("Dt:%f" % Dt)
        Dt1 = Dt + L * np.sin(alpha)

        # Add Dt1 to the buffer for smoothing
        self.dt1_buffer.append(Dt1)

        # Keep buffer size manageable (10 samples for 2 seconds @ 5 Hz)
        if len(self.dt1_buffer) > 10:
            self.dt1_buffer.pop(0)

        # Apply Butterworth filter if the buffer has sufficient data
        if len(self.dt1_buffer) > 1:
            smoothed_dt1 = self.butterworth_filter(self.dt1_buffer)[-1]
        else:
            smoothed_dt1 = Dt1  # Use raw Dt1 if insufficient data

        return (smoothed_dt1 - dist)

    def pid_control(self, error, velocity):
        """
        Calculate control outputs using the PID controller.
        """
        if self.dt>5:
            self.dt = 0.25
        self.error = error
        self.integral += error * self.dt
        self.differential = (error - self.prev_error) / self.dt

        # Cap the derivative term
        self.differential = max(min(self.differential, self.DERIVATIVE_CAP), -self.DERIVATIVE_CAP)

        # PID output
        steering_command = self.kp * self.error + self.ki * self.integral + self.kd * self.differential

        # Clamp steering angle to safe range
        max_steering_angle = np.pi * (45 / 180)
        steering_command = max(min(steering_command, max_steering_angle), -max_steering_angle)

        # Adjust throttle based on steering
        if np.abs(steering_command) <= 10:
            throttle_command = velocity
        elif np.abs(steering_command) <= 20:
            throttle_command = velocity - 0.004
        else:
            throttle_command = 0.001
        print(throttle_command)
        print(steering_command)
        # Publish messages
        self.current_velocity = throttle_command

        self.throttle_msg.data = float(throttle_command)
        self.throttle_publisher.publish(self.throttle_msg)

        self.steering_msg.data = float(steering_command)
        self.steering_publisher.publish(self.steering_msg)

        self.prev_error = error

    def scan_callback(self, msg):
        """
        Callback function for LaserScan messages. Calculate the error and publish the drive message.
        """
        current_time = msg.header.stamp.sec+msg.header.stamp.nanosec/(1e9)
        self.dt = current_time-self.previous_time
        self.previous_time = current_time
        desired_distance = 0.6 # Desired wall distance
        error = self.get_error(msg.ranges, desired_distance)  # Calculate error based on smoothed Dt1
        velocity = 0.008  # Set a constant velocity

        print("error: %f",error)

        # Use PID to control the car
        self.pid_control(error, velocity)


def main(args=None):
    rclpy.init(args=args)
    print("WallFollow Initialized")
    wall_follow_node = WallFollow()
    rclpy.spin(wall_follow_node)

    # Destroy the node explicitly
    wall_follow_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
