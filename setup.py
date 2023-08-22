# encoding=utf-8
import re
from os.path import join, dirname
from setuptools import setup, find_packages


def read_file_content(filepath):
    with open(join(dirname(__file__), filepath), encoding="utf8") as fp:
        return fp.read()


def find_version(filepath):
    content = read_file_content(filepath)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


VERSION = find_version(join("pcdet_open", "__init__.py"))
long_description = read_file_content("README.md")

setup(
    name="pcdet-open",
    version=VERSION,
    url="https://github.com/xtreme1-io/point-cloud-object-detection.git",
    author="Dasheng Ji",
    author_email="jidasheng@basicfinder.com",
    description="Point cloud object detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "requests",
        "python-lzf",
        "scikit-learn",
        "tornado",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
