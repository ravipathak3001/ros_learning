import math
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.action import RotateAbsolute

def normalize(a):
    return math.atan2(math.sin(a), math.cos(a))

class SmoothRotator(Node):
    def __init__(self):
        super().__init__('smooth_rotator')
        self.declare_parameter('kp',2.0)
        self.declare_parameter('max_speed', 2.0)
        self.pose = None

        group = ReentrantCallbackGroup()    # allow callback to run in parallel
        self.pub = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.sub = self.create_subscription(Pose, 'turtle1/pose', self.on_pose, 10, callback_group=group)

        self.server = ActionServer(
            self, RotateAbsolute, 'smooth_rotate',
            execute_callback=self.execute,
            goal_callback=self.on_goal,
            cancel_callback=self.on_cancel,
            callback_group=group)
        self.get_logger().info('Smooth rotator ready on /smooth_rotate')

    def on_pose(self, msg):
        self.pose = msg

    # 1) Decide whether to accept a new goal
    def on_goal(self, goal_request):
        if not -math.pi <= goal_request.theta <= math.pi:
            self.get_logger().warn('Rejected: theta must be between -pi and pi')
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    # 2) Decide whether to allow a cancel
    def on_cancel(self, goal_handle):
        self.get_logger().info('Cancel requested')
        return CancelResponse.ACCEPT

    # 3) Do the actual work
    def execute(self, goal_handle):
        while self.pose is None:
            time.sleep(0.05)
        target = goal_handle.request.theta
        start = self.pose.theta
        feedback = RotateAbsolute.Feedback()

        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                self.stop()
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return self.make_result(start)

            error = normalize(target - self.pose.theta)
            if abs(error) < 0.01:
                break

            kp = self.get_parameter('kp').value
            max_w = self.get_parameter('max_speed').value
            cmd = Twist()
            cmd.angular.z = max(-max_w, min(max_w, kp*error))
            self.pub.publish(cmd)

            feedback.remaining = error
            goal_handle.publish_feedback(feedback)
            time.sleep(0.05)

        self.stop()
        goal_handle.succeed()
        self.get_logger().info('Goal Succeeded')
        return self.make_result(start)

    def stop(self):
        self.pub.publish(Twist())

    def make_result(self, start):
        result = RotateAbsolute.Result()
        result.delta = normalize(self.pose.theta - start)
        return result

def main(args = None):
    rclpy.init(args=args)
    node=SmoothRotator()
    executor = MultiThreadedExecutor()
    try:
        rclpy.spin(node, executor=executor)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()