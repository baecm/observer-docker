"""
Starcraft BW docker launcher.
"""

# Always prefer setuptools over distutils
from setuptools import setup

from observer.defaults import VERSION

setup(
    name='observer',
    version=VERSION,
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['requests',
                      'coloredlogs',
                      'numpy',
                      'tqdm',
                      'requests',
                      'python-dateutil',
                      'pandas',
                      'matplotlib',
                      'docker'],
    packages=['observer'],
    entry_points={  # Optional
        'console_scripts': [
            'observer=observer.cli:main',
        ],
    },
    python_requires='>=3.4',
    include_package_data=True
)
