import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/workspaces/F1Tenth_Team_Clutch/CDC-2024-CLUTCH-DEVKIT/install/my_robot_controller'
