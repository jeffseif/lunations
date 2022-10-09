from setuptools import setup


__author__ = "Jeffrey Seifried"
__email__ = "jeffrey.seifried@gmail.com"
__program__ = "lunations"
__url__ = "http://github.com/jeffseif/{}".format(__program__)
__version__ = "1.0.0"


setup(
    author=__author__,
    author_email=__email__,
    install_requires=[
        "numpy",
        "pandas",
        "python-dateutil",
        "pytz",
        "scipy",
    ],
    name=__program__,
    packages=[__program__],
    url=__url__,
    version=__version__,
)
