#!/bin/bash

echo y | sudo apt update

echo y | wget -qO - http://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo apt-key add -

codename=$(lsb_release -sc)

echo y | sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-$codename.list http://packages.lunarg.com/vulkan/lunarg-vulkan-$codename.list

echo y | echo "Vulkan sources list has been downloaded for codename: $codename"

echo y | sudo apt update

echo y | sudo apt install vulkan-sdk

echo y | apt-get update

echo y | apt-get install -y mesa-vulkan-drivers mesa-vulkan-drivers

vulkaninfo 

