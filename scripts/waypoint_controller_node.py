#!/usr/bin/env python3
import math
import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_autonomous_mission.msg import MissionStatus
from turtle_autonomous_mission.srv import StartMission, StartMissionResponse

# =====================================================================
# DAFTAR WAYPOINT LEVEL 1 (MUDAH DIUBAH DI SATU TEMPAT)
# 4 Waypoint Sudut + 1 Waypoint Kembali ke Titik Awal (5.54, 5.54)
# =====================================================================
DEFAULT_WAYPOINTS = [
    [2.0, 2.0],
    [9.0, 2.0],
    [9.0, 9.0],
    [2.0, 9.0],
    [5.54, 5.54]
]

class WaypointPatrolController:
    def __init__(self):
        rospy.init_node('waypoint_controller_node', anonymous=False)

        # Ambil daftar waypoint dari parameter atau gunakan DEFAULT_WAYPOINTS
        self.waypoints = rospy.get_param('~waypoints', DEFAULT_WAYPOINTS)
        self.tolerance = 0.08  # Kriteria 1: Toleransi jarak < 0.1 unit

        # Konstanta Proporsional (P-Controller)
        self.kp_linear = 1.5
        self.kp_angular = 6.0
        self.max_linear = 2.0
        self.max_angular = 4.0

        self.pose = None
        self.wp_index = 0
        self.mission_active = True

        # Publisher & Subscriber
        self.cmd_pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
        self.status_pub = rospy.Publisher('/mission_status', MissionStatus, queue_size=10)
        self.pose_sub = rospy.Subscriber('/turtle1/pose', Pose, self.pose_callback)

        # Custom Service Server (/start_mission)
        self.srv = rospy.Service('/start_mission', StartMission, self.handle_start_mission)

        self.rate = rospy.Rate(20)
        rospy.loginfo("[Controller] Node Kendali Waypoint Level 1 Aktif!")

    def pose_callback(self, msg):
        self.pose = msg

    @staticmethod
    def normalize_angle(angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def stop_turtle(self):
        self.cmd_pub.publish(Twist())

    def handle_start_mission(self, req):
        if req.start:
            self.wp_index = 0
            self.mission_active = True
            return StartMissionResponse(True, "Misi Waypoint Patrol dimulai ulang dari Waypoint 1.")
        else:
            self.mission_active = False
            self.stop_turtle()
            return StartMissionResponse(True, "Misi Waypoint Patrol dihentikan sementara.")

    def move_to_waypoint(self, target_x, target_y):
        # Hitung jarak Euclidean ke titik target
        dx = target_x - self.pose.x
        dy = target_y - self.pose.y
        distance = math.sqrt(dx * dx + dy * dy)

        # Hitung sudut hadap menuju titik target
        desired_theta = math.atan2(dy, dx)
        angle_error = self.normalize_angle(desired_theta - self.pose.theta)

        cmd = Twist()
        # P-Controller untuk kecepatan putar (angular.z)
        cmd.angular.z = max(-self.max_angular, min(self.max_angular, self.kp_angular * angle_error))

        # P-Controller untuk kecepatan maju (linear.x)
        if abs(angle_error) < 0.4:
            v_lin = self.kp_linear * distance
            cmd.linear.x = max(0.0, min(self.max_linear, v_lin))
        else:
            cmd.linear.x = 0.0

        self.cmd_pub.publish(cmd)
        return distance

    def publish_status(self, wp_num, tx, ty, dist, text):
        msg = MissionStatus()
        msg.current_waypoint = wp_num
        msg.total_waypoints = len(self.waypoints)
        msg.target_x = float(tx)
        msg.target_y = float(ty)
        msg.distance_to_target = float(dist)
        msg.status_text = text
        self.status_pub.publish(msg)

    def run(self):
        while not rospy.is_shutdown():
            if self.pose is not None:
                if not self.mission_active:
                    self.stop_turtle()
                    self.publish_status(self.wp_index, 0.0, 0.0, 0.0, "PAUSED")
                elif self.wp_index < len(self.waypoints):
                    tx, ty = self.waypoints[self.wp_index]
                    dist = self.move_to_waypoint(tx, ty)

                    if dist < self.tolerance:
                        self.stop_turtle()
                        self.publish_status(self.wp_index + 1, tx, ty, dist, "WAYPOINT_REACHED")
                        self.wp_index += 1
                        rospy.sleep(0.5)
                    else:
                        self.publish_status(self.wp_index + 1, tx, ty, dist, "MOVING_TO_TARGET")
                else:
                    # Kriteria 2: Setelah waypoint terakhir tercapai, turtle1 berhenti
                    self.stop_turtle()
                    last_tx, last_ty = self.waypoints[-1]
                    self.publish_status(len(self.waypoints), last_tx, last_ty, 0.0, "MISSION_COMPLETED")
            self.rate.sleep()

if __name__ == '__main__':
    try:
        node = WaypointPatrolController()
        node.run()
    except rospy.ROSInterruptException:
        pass
