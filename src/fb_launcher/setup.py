from setuptools import setup
from pathlib import Path

package_name = 'fb_launcher'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', [str(Path('resource') / package_name)]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Tony Lu',
    maintainer_email='juncheng@andrew.cmu.edu',
    description='Frisbee launcher',
    license='MIT',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'launcher_node = fb_launcher.launcher_node:main',
        ],
    },
)