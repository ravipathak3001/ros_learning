import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from turtlesim.action import RotateAbsolute

class RotateClient(Node):
    def __init__(self):
        super().__init__('rotate_client')
        self.declare_parameter('theta', 1.57)
        self.declare_parameter('action_name', 'turtle1/rotate_absolute')
        self.declare_parameter('timeout', 1.0)
        self.done = False
        self.goal_handle = None
        self.cancel_timer = None
        name = self.get_parameter('action_name').value
        self.client = ActionClient(self, RotateAbsolute, name)

    def send_goal(self):
        goal = RotateAbsolute.Goal()
        goal.theta = float(self.get_parameter('theta').value)
        self.get_logger().info('waiting for action server ...')
        self.client.wait_for_server()
        self.get_logger().info(f'Sending Goal: theta={goal.theta: .2f}')
        future = self.client.send_goal_async(goal, feedback_callback=self.on_feedback)
        future.add_done_callback(self.on_goal_response)

    def on_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().warn('Goal Rejected')
            self.done = True
            return
        self.get_logger().info('Goal Accepted')
        self.goal_handle = handle
        timeout = self.get_parameter('timeout').value
        self.cancel_timer = self.create_timer(timeout, self.on_timeout)
        handle.get_result_async().add_done_callback(self.on_result)

    def on_timeout(self):
        self.cancel_timer.cancel()
        if self.done:
            return
        self.get_logger().warn('Timeout reached cancelling the goal')
        future = self.goal_handle.cancel_goal_async()
        future.add_done_callback(self.on_cancel_response)

    def on_cancel_response(self, future):
        response = future.result()
        if len(response.goals_canceling) > 0:
            self.get_logger().info('Cancel accepted, waiting for final result...')
        else:
            self.get_logger().info('Cancel, rejected (goal probably finished already)')


    def on_feedback(self, feedback_msg):
        self.get_logger().info(f'Remaining: {feedback_msg.feedback.remaining: .3f} rad')

    def on_result(self, future):
        if self.cancel_timer is not None:
            self.cancel_timer.cancel()
        response = future.result()
        status = {GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED',
                  GoalStatus.STATUS_CANCELED: 'CANCELED',
                  GoalStatus.STATUS_ABORTED: 'ABORTED'}.get(response.status, str(response.status))
        self.get_logger().info(f'Finished: {status}, rotated {response.result.delta: .2f} rad')
        self.done = True

def main(args=None):
    rclpy.init(args=args)
    node = RotateClient()
    node.send_goal()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
