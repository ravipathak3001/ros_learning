import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class WallBouncer(Node):
    def __init__(self):
        super().__init__('wall_bouncer')   #NODE NAME
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.sub = self.create_subscription(Pose, '/turtle1/pose', self.on_pose, 10)
        self.timer = self.create_timer(0.1, self.tick)
        self.get_logger().info('Wall Bouncer started')
        self.current_pose = {
    "x": 0,
    "y": 0,
    "theta": 0
}

    def tick(self):
        msg = Twist()
        if  self.current_pose["x"] > 11 or self.current_pose["x"] <= 0 or self.current_pose["y"] > 11 or self.current_pose["y"] <= 0:
            msg.angular.z = 2.0
            msg.linear.x = 0.2
        else:
            msg.linear.x = 1.0
            msg.angular.z = 0.0
        self.pub.publish(msg)

    def on_pose(self, msg:Pose):
        self.get_logger().info(
            f'x={msg.x:.2f} y={msg.y:.2f} theta={msg.theta:.2f}',
            throttle_duration_sec=1.0
        )
        self.current_pose = {
    "x": round(msg.x, 2),
    "y": round(msg.y, 2),
    "theta": round(msg.theta, 2)
}


def main(args=None):
    rclpy.init(args=args)
    node = WallBouncer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
    

