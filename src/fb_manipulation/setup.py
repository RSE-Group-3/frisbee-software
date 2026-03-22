from setuptools import setup
from pathlib import Path
from glob import glob

package_name = 'fb_manipulation'

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
    description='Frisbee hardware',
    license='MIT',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'manipulation_node = fb_manipulation.manipulation_node:main',
            'fake_arduino = fb_manipulation.fake_arduino:main',
        ],
    },
)