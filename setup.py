from setuptools import setup, find_packages

setup(
    name="noteiq",
    version="1.0.0",
    description="AI-Powered Notes Application",
    author="Himal Badu, AI Founder",
    author_email="himal@noteiq.app",
    url="https://github.com/himalbadu/noteiq",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.2",
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "httpx>=0.24.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "noteiq=cli.main:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)