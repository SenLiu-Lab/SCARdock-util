from setuptools import setup, find_packages
from pathlib import Path
import yaml

with open('meta.yaml', 'r') as file:
    doc = yaml.load(file, Loader=yaml.FullLoader)
    version = doc['package']['version']

here = Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='scardock-util',
    version=version,
    description='A Comprehensive Toolkit for SCARdock Covalent Docking and Molecular Modeling',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/SenLiu-Lab/SCARdock-util.git',
    author='lingyu zeng',
    author_email='pylyzeng@gmail.com',
    license='MIT License',
    classifiers=[
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["tools", "autodock vina", "scardock", "covalent docking"],
    packages=['scardock_util', 'scardock_util.vutils', 'scardock_util.pymolutils'],
    python_requires='>=3.9',
    install_requires=[],
    platforms=["linux-64"],
    entry_points={
        'console_scripts': [
            'scardock = scardock_util.scardock:SCARdock',
            'scardocktest = scardock_util.scardock:SCARdocktest'
        ],
    },
    package_data={
        'scardock_util': ['test/*'],
    }
)
