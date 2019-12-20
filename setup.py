#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Setup file for phd_scraper"""

from setuptools import setup, find_packages, Extension

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Cesar Aybar, Roy Yali, Antony Barja, Julio Contreras",
    author_email='csaybar@gmail.com, ryali93@gmail.com, antony.barja8@gmail.com, julius013199@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Scraping toolkit to generate PhD dataset",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='scraper',
    name='phd_scraper',
    packages=find_packages(include=['phd_scraper']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/csaybar/phd_scraper',
    version='0.1.3',
    zip_safe=False,
)