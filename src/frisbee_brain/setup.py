from setuptools import setup
from pathlib import Path

package_name = 'frisbee_brain'

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
        (str(Path('share') / package_name / 'launch'), get_launch_files()),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Tony Lu',
    maintainer_email='juncheng@andrew.cmu.edu',
    description='Central Planner Nodes for coordinating frisbee robot subsystems',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'state_machine = frisbee_brain.state_machine:main',
            'central_planner = frisbee_brain.central_planner:main',
        ],
    },
)