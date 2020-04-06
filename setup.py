#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("src/comp_etag/version.py") as f:
    exec(f.read())

setup(
    name="compETAG",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="The tool provides methods to calculate ETags for Objects on AWS S3, "
    "and also md5s, on local objects. It also allows to check the "
    "integrity of files, both locally and on AWS S3.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/awnimo/compETAG",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    scripts=["src/compute_etags"],
    install_requires=["numpy", "boto3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
