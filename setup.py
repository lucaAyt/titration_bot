# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import details

dependecies = open('requirements.txt', 'r').read().splitlines()
version = open('version', 'r').read().strip()

setup(
    name=details.name,
    version=version,
    description=details.brief_description,
    author="Luca Bertossi",
    author_email="lucabertossi@gmail.com",
    package_dir={'': 'src'},
    packages=[''] + find_packages("src"),
    python_requires=">=3.7, <4",
    install_requires=[dependecies],
    extras_require={
    }
)
