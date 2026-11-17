# Turtle Autonomous Mission - Level 1 (Waypoint Patrol)

Package ROS 1 Noetic (`turtle_autonomous_mission`) untuk menggerakkan `turtle1` secara otonom mengunjungi daftar waypoint berurutan menggunakan P-Controller berbasis umpan balik `/turtle1/pose`.

## Level yang Diselesaikan
- **Level 1 – Waypoint Patrol**:
  1. `turtle1` bergerak otomatis ke 5 titik waypoint (4 titik sudut + kembali ke titik awal tengah) dan berhenti di tiap titik dengan toleransi jarak `< 0.1` unit (`0.08` unit).
  2. Setelah waypoint terakhir tercapai, `turtle1` berhenti.
  3. Daftar waypoint tersimpan di satu tempat pada parameter `waypoints` di `mission.launch` dan list `DEFAULT_WAYPOINTS`.

## Cara Build dan Menjalankan Program
1. Build package:
   cd ~/catkin_ws
   catkin_make
   source ~/catkin_ws/devel/setup.bash

2. Jalankan dengan satu perintah roslaunch:
   roslaunch turtle_autonomous_mission mission.launch

## Penjelasan Arsitektur ROS
- **Node 1 (`waypoint_controller_node.py`)**: Membaca posisi dari `/turtle1/pose`, menghitung kecepatan menggunakan P-Controller, mengirim perintah gerak ke `/turtle1/cmd_vel`, menyediakan service `/start_mission`, dan mengirim status misi ke topic `/mission_status`.
- **Node 2 (`mission_monitor_node.py`)**: Subscribe ke topic `/mission_status` untuk memantau dan mencetak jarak ke target serta pencapaian tiap waypoint.
- **Custom Message (`MissionStatus.msg`)**: Berisi `current_waypoint`, `total_waypoints`, `target_x`, `target_y`, `distance_to_target`, dan `status_text`.
- **Custom Service (`StartMission.srv`)**: Service `/start_mission` dengan request `bool start` dan response `bool success`, `string message` untuk memulai ulang atau menghentikan misi.
