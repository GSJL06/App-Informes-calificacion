"""
Setup script para DOCX Editor
Instalación: pip install -e .
"""
from setuptools import setup, find_packages
from pathlib import Path

# Leer README
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

# Leer requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line.split("==")[0])

setup(
    name="docx-editor",
    version="1.0.0",
    author="DOCX Editor Team",
    author_email="support@example.com",
    description="Editor profesional de archivos DOCX con enfoque en pies de página y placeholders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/docx-editor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.9",
    install_requires=[
        "python-docx>=1.0.0",
        "lxml>=5.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.5",
        "click>=8.0.0",
        "tqdm>=4.60.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "docx-editor=cli.commands:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
