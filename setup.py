import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = "1.0dev1"

setup(
    name='rawlogs',
    author="Andrea Censi",
    author_email="censi@mit.edu",
    url='http://github.com/AndreaCensi/rawlogs',
    version=version,
    description="Abstractions over log sources",

    long_description=read('README.md'),
    keywords="",
    license="LGPL",

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU Library or '
        'Lesser General Public License (LGPL)',
    ],

    package_dir={'':'src'},
    packages=find_packages('src'),
    entry_points={
     'console_scripts': [
       'rawlogs = rawlogs.programs:rawlogs_main'
      ]
    },
    install_requires=[
        'QuickApp',
        'PyContracts',
        'ConfTools',
    ],

    tests_require=['nose']
)

