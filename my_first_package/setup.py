import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'my_first_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sun-tzu',
    maintainer_email='sun-tzu@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'circle_driver = my_first_package.circle_driver:main',
            'pose_watcher = my_first_package.pose_watcher:main',
            'wall_bouncer = my_first_package.wall_bouncer:main',
            'rotate_client = my_first_package.rotate_client:main',
            'smooth_rotator = my_first_package.smooth_rotator:main'
        ],
    },
)
