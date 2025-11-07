"""Setup script for restack-gen CLI.

This file provides backward compatibility with older pip versions.
For modern installations, use pyproject.toml directly.
"""

from setuptools import find_packages, setup

setup(
    name="restack-gen",
    packages=find_packages(),
    include_package_data=True,
)
