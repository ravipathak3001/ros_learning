import math
import random
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import TeleportAbsolute
from turtlesim.srv import SetPen
from std_srvs.srv import SetBool
from rcl_interfaces.msg import SetParametersResult

MAX_XY = 11.0
CENTER = 5.5

def normalize(angle):
    return math.atan2(math.sin(angle), math.cos(angle))

class WallBouncer(Node):
    def __init__(self):

        super().__init__('wall_bouncer')   #NODE NAME
        
        # --- state ---
        self.pose = None
        self.turning = False
        self.paused = False
        self.target_heading = 0.0

        # --- parameters ---
        self.declare_parameter('margin', 1.0)
        self.declare_parameter('drive_speed', 2.0)
        self.declare_parameter('turn_speed', 3.0)
        self.add_on_set_parameters_callback(self.on_params)

        # --- topics ---
        self.pub = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.sub = self.create_subscription(Pose, 'turtle1/pose', self.on_pose, 10)

        # --- service server ---
        self.serv = self.create_service(SetBool, 'set_paused', self.on_set_paused)
        

        # --- service client start fro, the center ---
        self.teleport_cli = self.create_client(TeleportAbsolute, 'turtle1/teleport_absolute')
        self.pen_cli = self.create_client(SetPen, 'turtle1/set_pen')

        if self.teleport_cli.wait_for_service(timeout_sec=5.0):
            req = TeleportAbsolute.Request()
            req.x, req.y, req.theta = CENTER, CENTER, random.uniform(-math.pi, math.pi)
            future = self.teleport_cli.call_async(req)
            future.add_done_callback(lambda f: self.get_logger().info('Teleported to centre'))
        else:
            self.get_logger().info('Teleport seervice not available, starting where I am')
        self.set_pen(0,255,0)
        self.timer = self.create_timer(0.1, self.tick)
        self.get_logger().info('Wall Bouncer started')

    # --- callbacks ---
    def on_params(self, params):
        for p in params:
            if p.name in ('margin', 'drive_speed', 'turn_speed') and p.value <= 0.0:
                return SetParametersResult(successful=False, reason=f'{p.name} must be > 0')
        return SetParametersResult(successful=True)

    def on_set_paused(self, request, response):
        self.paused = request.data
        response.success = True
        response.message = 'Paused' if self.paused else 'Resumed'
        self.get_logger().info(response.message)
        return response

    def on_pose(self, msg:Pose):
        self.pose = msg
        self.get_logger().info(
                    f'x={msg.x:.2f} y={msg.y:.2f} theta={msg.theta:.2f}',
                    throttle_duration_sec=1.0
                )

    # --- logic ---
    def heading_into_wall(self, margin) -> bool:
        p = self.pose
        dx, dy = math.cos(p.theta), math.sin(p.theta)
        return ((p.x > MAX_XY - margin and dx > 0) or
                (p.x < margin and dx < 0) or
                (p.y > MAX_XY - margin and dy > 0) or
                (p.y < margin and dy < 0))
    
    # --- helper function ---
    def set_pen(self, r,g,b):
        req = SetPen.Request()
        req.r, req.g, req.b = r,g,b
        req.width = 3
        req.off = 0
        self.pen_cli.call_async(req)

    def tick(self):
        msg = Twist()
        if self.pose is None or self.paused:
            self.pub.publish(msg)
            return

        margin = self.get_parameter('margin').value
        drive = self.get_parameter('drive_speed').value
        turn = self.get_parameter('turn_speed').value
        p = self.pose

        if self.turning:
            error = normalize(self.target_heading - p.theta)
            if(abs(error) < 0.1):
                self.turning = False
                self.set_pen(255,0,0)
            else:
                msg.angular.z = turn if error > 0 else -turn
        elif self.heading_into_wall(margin):
            to_center = math.atan2(CENTER - p.y, CENTER - p.x)
            self.target_heading = normalize(to_center + random.uniform(-0.6, 0.6))
            self.turning = True
            self.set_pen(0,255,0)
        else:
            msg.linear.x = drive

        self.pub.publish(msg)


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
    

