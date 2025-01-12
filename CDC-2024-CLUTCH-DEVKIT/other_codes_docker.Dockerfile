# Copy AutoDRIVE Devkit (ROS 2 API)
RUN [ -d /home/clutch_autodrive ] && mkdir /home/clutch_autodrive/src || echo "/home/clutch_autodrive does not exist"
RUN cd /home/clutch_autodrive && colcon build
RUN /bin/bash -c 'echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc' \
    && /bin/bash -c 'echo "source /home/clutch_autodrive/install/setup.bash" >> ~/.bashrc' \
    && /bin/bash -c 'source ~/.bashrc'

# Set work directory and expose port
WORKDIR /home/clutch_autodrive
EXPOSE 4567

# Set entrypoint
#COPY autodrive_devkit.sh /home
#ENTRYPOINT ["/home/autodrive_devkit.sh"]

ENV DISPLAY=:1
# ENV DISPLAY=host.docker.internal:1
