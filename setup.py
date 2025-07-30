from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name="afry-img2ifc",
    version="1.0.0",
    author="AFRY",
    author_email="your.email@afry.com",
    description="A tool to convert images with GPS data to IFC markers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rosbache/afry-img2ifc",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: AEC Industry",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'afry-img2ifc=main:main',
            'afry-img2ifc-gui=src.gui.main_window:main',
        ],
    },
    include_package_data=True,
)
