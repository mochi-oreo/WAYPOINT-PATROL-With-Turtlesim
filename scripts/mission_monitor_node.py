#!/usr/bin/env python3
import rospy
from turtle_autonomous_mission.msg import MissionStatus

class MissionMonitorNode:
    def __init__(self):
        rospy.init_node('mission_monitor_node', anonymous=False)
        self.last_wp_logged = 0
        self.completed_logged = False
        self.sub = rospy.Subscriber('/mission_status', MissionStatus, self.status_callback)
        rospy.loginfo("[Monitor] Node Pemantau Status Misi Aktif!")

    def status_callback(self, msg):
        if msg.status_text == "MOVING_TO_TARGET":
            rospy.loginfo_throttle(
                1.5,
                f"[Monitor] Menuju Waypoint {msg.current_waypoint}/{msg.total_waypoints} "
                f"({msg.target_x:.2f}, {msg.target_y:.2f}) | Jarak: {msg.distance_to_target:.3f}"
            )
        elif msg.status_text == "WAYPOINT_REACHED" and msg.current_waypoint != self.last_wp_logged:
            self.last_wp_logged = msg.current_waypoint
            rospy.loginfo(
                f"[Monitor] BERHASIL! Waypoint {msg.current_waypoint}/{msg.total_waypoints} "
                f"tercapai dengan sisa jarak {msg.distance_to_target:.4f} (< 0.1 unit)."
            )
        elif msg.status_text == "MISSION_COMPLETED" and not self.completed_logged:
            self.completed_logged = True
            rospy.loginfo("[Monitor] MISI LEVEL 1 SELESAI! Seluruh waypoint telah dikunjungi dan turtle1 berhenti.")
        elif msg.status_text == "MOVING_TO_TARGET" and self.completed_logged:
            self.completed_logged = False
            self.last_wp_logged = 0

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        monitor = MissionMonitorNode()
        monitor.run()
    except rospy.ROSInterruptException:
        pass
