import rclpy
from rclpy.node import Node

from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import (
    Pose,
    PoseStamped,
    PoseWithCovariance,
    PoseWithCovarianceStamped,
)
from geometry_msgs.msg import Point
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy


class trajectoryPath(Node):

    # =====================================
    #         Class constructor
    #  Initializes node and subscribers
    # =====================================
    def __init__(self):
        super().__init__('pose_to_path')

        self.loadParams()
        self.trajectory_path_msg = Path()
        self.previous_pose_position = Point()

        qos_best_effort = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )
        qos_reliable = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )
        # Setup trajectory path publisher
        self.trajectory_path_pub = self.create_publisher(
            Path, 'trajectory_path', qos_reliable
        )
        # Setup subscriber to pose
        self.pose_sub = self.create_subscription(
            Pose, 'pose_topic', self.pose_callback, qos_best_effort
        )
        # Setup subscriber to pose stamped
        self.pose_stamped_sub = self.create_subscription(
            PoseStamped,
            'pose_stamped_topic',
            self.pose_stamped_callback,
            qos_best_effort,
        )
        # Setup subscriber to pose with covariance
        self.pose_cov_sub = self.create_subscription(
            PoseWithCovariance,
            'pose_cov_topic',
            self.pose_cov_callback,
            qos_best_effort,
        )
        # Setup subscriber to pose with covariance stamped
        self.pose_cov_stamped_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            'pose_cov_stamped_topic',
            self.pose_cov_stamped_callback,
            qos_best_effort,
        )
        # Setup subscriber to odometry
        self.odom_sub = self.create_subscription(
            Odometry, 'odom_topic', self.odom_callback, qos_best_effort
        )

    # =====================================
    #       function for loading
    #    from ROS parameter server
    # =====================================
    def loadParams(self):
        # Load maximum number of poses in actual path
        self.declare_parameter('max_poses', 1000)
        self.max_poses = (
            self.get_parameter('max_poses').get_parameter_value().integer_value
        )
        # Load threshold for adding a pose to actual path
        self.declare_parameter('movement_threshold', 0.001)
        self.threshold = (
            self.get_parameter('movement_threshold').get_parameter_value().double_value
        )
        # Load parent frame id for the trajectory
        self.declare_parameter('frame_id', 'map')
        self.frame_id = (
            self.get_parameter('frame_id').get_parameter_value().string_value
        )

    # =====================================
    #          Callback function
    #     when receiving pose message
    # =====================================
    def pose_callback(self, pose_msg):
        self.get_logger().debug(
            "received pose message with position: " + str(pose_msg.position)
        )
        # Process message position and add it to path
        self.publish_trajectory_path(pose_msg.position)

    # =====================================
    #      Callback function when
    #  receiving stamped pose message
    # =====================================
    def pose_stamped_callback(self, pose_stamped_msg):
        self.get_logger().debug(
            "received pose message with position: "
            + str(pose_stamped_msg.pose.position)
        )
        # Process message position and add it to path
        if pose_stamped_msg.header.frame_id == self.frame_id:
            self.publish_trajectory_path(pose_stamped_msg.pose.position)
        else:
            self.get_logger().error(
                "PoseStamped message frame:"
                + pose_stamped_msg.header.frame_id
                + " does not correspond to trajectory frame"
                + self.frame_id
            )

    # =====================================
    #      Callback function when
    #  receiving pose with cov message
    # =====================================
    def pose_cov_callback(self, pose_cov_msg):
        self.get_logger().debug(
            "received pose cov message with position: "
            + str(pose_cov_msg.pose.position)
        )
        # Process message position and add it to path
        self.publish_trajectory_path(pose_cov_msg.pose.position)

    # =====================================
    #      Callback function when
    #  receiving stamped pose cov message
    # =====================================
    def pose_cov_stamped_callback(self, pose_cov_stamped_msg):
        self.get_logger().debug(
            "received pose message with position: "
            + str(pose_cov_stamped_msg.pose.pose.position)
        )
        # Process message position and add it to path
        if pose_cov_stamped_msg.header.frame_id == self.frame_id:
            self.publish_trajectory_path(pose_cov_stamped_msg.pose.pose.position)
        else:
            self.get_logger().error(
                "PoseWithCovaranceStamped message frame:"
                + pose_cov_stamped_msg.header.frame_id
                + " does not correspond to trajectory frame"
                + self.frame_id
            )

    # =====================================
    #      Callback function when
    #  receiving odometry message
    # =====================================
    def odom_callback(self, odom_msg):
        self.get_logger().debug(
            "received odom message with position: " + str(odom_msg.pose.pose.position)
        )
        # Process message position and add it to path
        if odom_msg.header.frame_id == self.frame_id:
            self.publish_trajectory_path(odom_msg.pose.pose.position)
        else:
            self.get_logger().error(
                "Odometry message frame:"
                + odom_msg.header.frame_id
                + " does not correspond to trajectory frame "
                + self.frame_id
            )

    # =====================================
    #        Add pose and publish
    #      trajectory path message
    # =====================================
    def publish_trajectory_path(self, position):
        # If the pose has move more than a set threshold, add it to the path message and publish
        if (
            (abs(self.previous_pose_position.x - position.x) > self.threshold)
            or (abs(self.previous_pose_position.y - position.y) > self.threshold)
            or (abs(self.previous_pose_position.z - position.z) > self.threshold)
        ):
            self.get_logger().debug('Exceding threshold, adding pose to path')

            # Add current pose to path
            self.trajectory_path_msg.header.stamp = self.get_clock().now().to_msg()
            self.trajectory_path_msg.header.frame_id = self.frame_id
            pose_stamped_msg = PoseStamped()
            pose_stamped_msg.header.stamp = self.get_clock().now().to_msg()
            pose_stamped_msg.pose.position.x = position.x
            pose_stamped_msg.pose.position.y = position.y
            pose_stamped_msg.pose.position.z = position.z
            pose_stamped_msg.pose.orientation.w = 1.0

            # If max number of poses in path has not been reach, just add pose to message
            if len(self.trajectory_path_msg.poses) < self.max_poses:
                self.trajectory_path_msg.poses.append(pose_stamped_msg)
            # Else rotate the list to dismiss oldest value and add newer value at the end
            else:
                self.get_logger().debug(
                    'Max number of poses reached, erasing oldest pose'
                )
                self.trajectory_path_msg.poses = self.trajectory_path_msg.poses[1:]
                self.trajectory_path_msg.poses.append(pose_stamped_msg)

            self.previous_pose_position = pose_stamped_msg.pose.position
            self.trajectory_path_pub.publish(self.trajectory_path_msg)


def main(args=None):
    rclpy.init(args=args)

    trajectory_path = trajectoryPath()

    rclpy.spin(trajectory_path)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    trajectory_path.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
