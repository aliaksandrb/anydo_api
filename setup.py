#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'requests>=2.8.0'
]

test_requirements = [
    'vcrpy>=1.7.3'
]

setup(
    name='anydo_api',
    version='0.0.1',
    description="Unofficial AnyDo API wrapper for Python",
    long_description=readme + '\n\n' + history,
    author="Aliaksandr Buhayeu",
    author_email='aliaksandr.buhayeu@gmail.com',
    url='https://github.com/aliaksandrb/anydo_api',
    packages=[
        'anydo_api',
    ],
    package_dir={'anydo_api':
                 'anydo_api'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='anydo, anydo_api, api',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
