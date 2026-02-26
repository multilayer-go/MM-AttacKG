"""Package setup configuration."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="mm-attackg",
    version="0.1.0",
    author="MM-AttacKG Contributors",
    author_email="your.email@example.com",
    description="Multimodal Attack Knowledge Graph Construction from CTI Reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/MM-AttacKG",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "openai>=1.0.0",
        "dashscope>=1.14.0",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "PyYAML>=6.0.0",
        "python-dotenv>=1.0.0",
        "colorlog>=6.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "pylint>=2.17.5",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mm-attackg-single=src.run_single_cti:main",
            "mm-attackg-batch=src.run_all_cti:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json"],
    },
)
