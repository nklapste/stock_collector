#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""setup.py for stock-collector"""

from setuptools import find_packages, setup

setup(
    name="stock-collector",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "yfinance>=0.1.54,<2.0.0",
        "pandas>=0.25.3,<1.0.0",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    entry_points={
        "console_scripts": ["stock-collector = stock_collector.__main__:main"]
    },
)
