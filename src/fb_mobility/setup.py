from setuptools import setup
from pathlib import Path
from glob import glob

package_name = 'fb_mobility'

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
    maintainer='Michelle Liu',
    maintainer_email='mmliu@andrew.cmu.edu',
    description='',
    license='MIT',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'diff_drive = fb_mobility.diff_drive:main',
        ],
    },
)