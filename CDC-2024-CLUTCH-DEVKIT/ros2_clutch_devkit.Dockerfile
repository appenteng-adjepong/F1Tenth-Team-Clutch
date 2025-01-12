####################################################
#
#   AutoDRIVE Devkit Dockerfile
#
####################################################

# Set base image
FROM osrf/ros:humble-desktop

# Install Debian packages
RUN apt update \
    && apt install -y --no-install-recommends \
        sudo \
        wget \
        gedit \
        nano \
        vim \
        curl \
        unzip \
        net-tools \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install attrdict
RUN pip3 install numpy
RUN pip3 install pillow
RUN pip3 install opencv-contrib-python
RUN pip3 install eventlet==0.33.3
RUN pip3 install Flask==1.1.1
RUN pip3 install Flask-SocketIO==4.1.0
RUN pip3 install python-socketio==4.2.0
RUN pip3 install python-engineio==3.13.0
RUN pip3 install greenlet==1.1.0
RUN pip3 install gevent==21.12.0
RUN pip3 install gevent-websocket==0.10.1
RUN pip3 install Jinja2==3.0.3
RUN pip3 install itsdangerous==2.0.1
RUN pip3 install werkzeug==2.0.3
RUN pip3 install transforms3d

# Install ROS 2 dependencies
RUN apt update && apt install -y --no-install-recommends \
    ros-$ROS_DISTRO-tf-transformations \
    ros-$ROS_DISTRO-imu-tools

# Install tools for display
RUN apt update --fix-missing \
    && apt install -y xvfb ffmpeg libgdal-dev libsm6 libxext6 x11-apps

# Setup ROS2 API for each terminal session
RUN /bin/bash -c 'echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc'
RUN /bin/bash -c 'echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ~/.bashrc'
RUN /bin/bash -c 'echo "source /workspaces/F1Tenth_Team_Clutch/CDC-2024-CLUTCH-DEVKIT/install/setup.bash" >> ~/.bashrc'
RUN sudo apt install -y python3-colcon-common-extensions

