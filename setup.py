from setuptools import setup, find_packages

setup(
    name="aternos-auto-booster",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.1",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "colorama>=0.4.6",
        "Flask>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "aternos-booster=src.main:main",
        ],
    },
    author="Aternos Booster",
    description="Auto click +1 button on Aternos server every minute",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)
