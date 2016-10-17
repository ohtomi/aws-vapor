# -*- coding: utf-8 -*-

import codecs
from os import path
from setuptools import find_packages
from setuptools import setup

VERSION = '0.0.10'


def load_long_description():
    return codecs.open(
        path.join(path.abspath(path.dirname(__file__)), 'README.rst'),
        mode='r',
        encoding='utf-8'
    ).read()


def load_install_requires():
    return [
        name.rstrip()
        for name in codecs.open(
            path.join(path.abspath(path.dirname(__file__)), 'requirements.txt'),
            mode='r',
            encoding='utf-8'
        ).readlines()
    ]


def load_test_require():
    return [
        name.rstrip()
        for name in codecs.open(
            path.join(path.abspath(path.dirname(__file__)), 'requirements-test.txt'),
            mode='r',
            encoding='utf-8'
        ).readlines()
    ]


def main():
    setup(
        name='aws-vapor',
        version=VERSION,
        description='Generates AWS CloudFormation template from python object',
        long_description=load_long_description(),
        author='Kenichi Ohtomi',
        author_email='ohtomi.kenichi@gmail.com',
        url='https://github.com/ohtomi/aws-vapor/',
        download_url='https://github.com/ohtomi/aws-vapor/tarball/v{0}'.format(VERSION),
        keywords='aws cloudformation template generator',
        packages=find_packages(),
        install_requires=load_install_requires(),
        test_require=load_test_require(),
        test_suite='nose.collector',
        entry_points={
            'console_scripts':
                'aws-vapor = aws_vapor.main:main',
            'aws_vapor.command': [
                'config = aws_vapor.configure:Configure',
                'get = aws_vapor.downloader:Downloader',
                'generate = aws_vapor.generator:Generator',
            ]
        },
        zip_safe=False,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ],
    )


if __name__ == '__main__':
    main()
