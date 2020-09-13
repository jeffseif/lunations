from setuptools import setup

from lunations import __author__
from lunations import __email__
from lunations import __program__
from lunations import __url__
from lunations import __version__


setup(
    author=__author__,
    author_email=__email__,
    install_requires=[],
    name=__program__,
    packages=[__program__],
    platforms='all',
    setup_requires=[
        'setuptools',
    ],
    url=__url__,
    version=__version__,
)
