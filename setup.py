from setuptools import setup, find_packages

setup(
    name="safewalk",
    version="1.0.0",
    description="SafeWalk - Trygg promenad-app med GPS-delning",
    author="SafeWalk Team",
    license="MIT",
    packages=find_packages(),
    package_data={"": ["data/*.json"]},
    data_files=[
        ("share/applications", ["safewalk.desktop"]),
    ],
    entry_points={
        "console_scripts": [
            "safewalk=safewalk.app:main",
        ],
    },
    python_requires=">=3.8",
    install_requires=[
        "PyGObject>=3.42",
    ],
)
