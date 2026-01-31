from setuptools import setup


__author__ = "Jeffrey Seifried"
__email__ = "jeffrey.seifried@gmail.com"
__program__ = "lunations"
__url__ = "http://github.com/jeffseif/{}".format(__program__)
__version__ = "1.0.1"


setup(
    author=__author__,
    author_email=__email__,
    install_requires=[],
    name=__program__,
    packages=[__program__],
    package_data={"": ["../dat/*.json.gz"]},
    url=__url__,
    version=__version__,
)
