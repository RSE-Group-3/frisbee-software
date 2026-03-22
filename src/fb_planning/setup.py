from setuptools import setup
from pathlib import Path
from glob import glob

package_name = 'fb_planning'

def get_launch_files():
    launch_dir = Path('launch')
    return [str(p) for p in launch_dir.glob('*.launch.py')]

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', [str(Path('resource') / package_name)]),
        ('share/' + package_name, ['package.xml']),

        ('share/' + package_name + '/launch', glob(package_name + '/launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Tony Lu',
    maintainer_email='juncheng@andrew.cmu.edu',
    description='Frisbee planning',
    license='MIT',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'central_planner = fb_planning.task_planning.central_planner:main',
        ],
    },
)