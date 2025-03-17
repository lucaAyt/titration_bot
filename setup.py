from setuptools import setup, find_packages
import info

dependecies = open('requirements.txt', 'r').read().splitlines()
version = open('version', 'r').read().strip()

setup(
    name=info.name,
    version=version,
    description=info.brief_description,
    author="Luca Bertossi",
    author_email="lucabertossi@gmail.com",
    package_dir={'': 'src'},
    packages=find_packages(where="src"),
    python_requires=">=3.7, <4",
    install_requires=[dependecies],
    extras_require={
    }
)
