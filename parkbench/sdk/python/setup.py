"""
Setup script for ParkBench Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="parkbench-sdk",
    version="0.1.0",
    author="ParkBench Team",
    author_email="team@parkbench.dev",
    description="Python SDK for the ParkBench AI agent platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/parkbench/parkbench",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.1",
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "crypto": [
            "cryptography>=3.4.8",
        ],
    },
    keywords="ai agent platform api sdk parkbench",
    project_urls={
        "Bug Reports": "https://github.com/parkbench/parkbench/issues",
        "Source": "https://github.com/parkbench/parkbench",
        "Documentation": "https://docs.parkbench.dev",
    },
) 