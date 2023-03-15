from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

setup(
    name="news-summarizer",
    version="0.1.0",
    description="A simple news article summarizer",
    author="LiterallyBlah",
    url="https://github.com/LiterallyBlah/The-Register-Article-Summariser-GUI",
    packages=find_packages(),
    install_requires=[
    'requests',
    'beautifulsoup4',
    'openai',
    'ttkthemes'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
   entry_points={
    'console_scripts': [
        'news-summarizer = news_summarizer.news_summarizer:main',
        ],
    },
)
