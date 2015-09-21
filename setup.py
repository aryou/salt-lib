import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Singlehop Salt-Lib",
    version = "0.1",
    author = "Aaron Ryou",
    author_email = "dev@singlehop.com",
    description = ("Salt Master Scripts and Dependencies"),
    license = "BSD",
    keywords = "Salt Master Singlehop",
    url = "https://github.com/singlehopllc",
    packages=find_packages(),
    long_description=read('README'),
    classifiers=[
        "Development Status :: Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires = ['pika>=0.10.0'],
)