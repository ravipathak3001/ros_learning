import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CircleDriver(Node):
    def __init__(self):
        super().__init__('circle_driver')   #node name
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel',10)
        self.timer = self.create_timer(0.1, self.tick) # call tick() every 0.1 sec (10Hz)
        self.get_logger().info('Circle driver started')
    
    def tick(self):
        msg = Twist()
        msg.linear.x = 2.0 #FARWARD SPEED
        msg.angular.z = 1.0 #TURNING SPEED
        self.pub.publish(msg)
    
def main(args=None):
    rclpy.init(args=args)
    node=CircleDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()