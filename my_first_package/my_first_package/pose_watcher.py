import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

class PoseWatcher(Node):
    def __init__(self):
        super().__init__('pose_watcher')
        self.sub = self.create_subscription(Pose, 'turtle1/pose', self.on_pose, 10)

    def on_pose(self, msg:Pose):
        # pose arrivert ~60 times/sec, so log at most once per sec
        self.get_logger().info(
            f'x={msg.x:.2f} y={msg.y:.2f} theta={msg.theta:.2f}',
            throttle_duration_sec=1.0)

def main(args=None):
    rclpy.init(args=args)
    node = PoseWatcher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        node.try_shutdown()