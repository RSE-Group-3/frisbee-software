from setuptools import setup
from pathlib import Path

package_name = 'frisbee_collector'

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
    description='Hardware interface for the frisbee collector/intake mechanism',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'collector_node = frisbee_collector.collector_node:main',
        ],
    },
)