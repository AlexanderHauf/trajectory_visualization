from setuptools import find_packages, setup
from glob import glob

package_name = 'tracking_visualization'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/' + package_name,
            ['package.xml'],
        ),
        (
            'share/' + package_name + '/launch',
            glob('launch/*.py'),
        ),
        (
            'share/' + package_name + '/rviz',
            glob('rviz/*.rviz'),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Robin Baran',
    maintainer_email='r-baran@hotmail.fr',
    description='The package for visualizing trajectories from a stream of pose or odometry\
        messages',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'tracking_visualization = tracking_visualization.trajectory_visualization:main',
        ],
    },
)
