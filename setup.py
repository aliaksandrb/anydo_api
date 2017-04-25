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
    'requests>=2.8.0',
    'six>=1.10.0'
]

test_requirements = [
    'vcrpy>=1.7.3'
]

extras_require = {
    ':python_version in "2.7"': ['contextlib2', 'mock'],
}

setup(
    name='anydo_api',
    version='0.0.2',
    description="Unofficial AnyDo API client in object-oriented style.",
    long_description=readme + '\n\n' + history,
    author="Aliaksandr Buhayeu",
    author_email='aliaksandr.buhayeu@gmail.com',
    url='https://github.com/aliaksandrb/anydo_api',
    packages=[
        'anydo_api',
    ],
    package_dir={'anydo_api': 'anydo_api'},
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    license="MIT",
    zip_safe=False,
    keywords='anydo, anydo_api, anydo_client',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities'

    ],
    test_suite='tests',
    tests_require=test_requirements
)
