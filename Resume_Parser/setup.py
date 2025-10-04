from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="resume-parser",
    version="1.0.0",
    author="Sarthak Chandervanshi",
    author_email="54674615+SarthakChandervanshi@users.noreply.github.com",
    description="A Python library for extracting links and text content from PDF resumes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SarthakChandervanshi/resume-parser",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pymupdf>=1.23.0",
    ],
    extras_require={
        "dev": [
            "black>=23.0.0",
            "pytest>=7.0.0",
        ],
    },
)
