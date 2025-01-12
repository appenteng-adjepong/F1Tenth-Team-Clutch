from setuptools import find_packages, setup

package_name = 'my_robot_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [ 
            "test_node = my_robot_controller.my_first_node:main",
            "draw_circle = my_robot_controller.draw_circle:main",
            "drive_vehicle1 = my_robot_controller.drive_vehicle1:main",
            "drive_vehicle2 = my_robot_controller.drive_vehicle2:main",
            "drive_vehicle3 = my_robot_controller.drive_vehicle3:main",
            "new_bridge = my_robot_controller.new_bridge:main",
            "my_subscriber_node = my_robot_controller.my_subscriber_node:main",
            # Don't forget to colcon build  with --symlink-install since it's a new executable
        ],
    },
)
