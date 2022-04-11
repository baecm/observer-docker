"""
Starcraft BW docker launcher.
"""

# Always prefer setuptools over distutils
from setuptools import setup

from scbw.defaults import VERSION


setup(
    name='scbw-cog',
    version=VERSION,
    description='Multi-platform Version of StarCraft: Brood War in a Docker Container',
    url='https://github.com/baecm/sc-docker',
    author='Cheong-mok Bae',
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

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
    ],
    keywords='starcraft docker broodwar ai bot',
    install_requires=['requests',
                      'coloredlogs',
                      'numpy',
                      'tqdm',
                      'requests',
                      'python-dateutil',
                      'pandas',
                      'matplotlib',
                      'docker'],
    # packages=['scbw'],
    entry_points={  # Optional
        'console_scripts': [
            'scbw-cog.play=scbw.cli:main',
        ],
    },
    python_requires='>=3.4',
    include_package_data=True
)
