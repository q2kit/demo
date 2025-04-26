from setuptools import setup, find_packages

setup(
    name="demo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "demo=demo.cli:main",
        ],
    },
    author="Q2k",
    author_email="q2k@q2k.dev",
    description="Reverse SSH CLI Tool with Remote Management",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/q2kit/demo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
