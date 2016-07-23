from os import path
from setuptools import setup, find_packages
import codecs


setup(
    name='aws-vapor',
    version='0.0.2',
    description='Generates AWS CloudFormation template from python object',
    long_description=codecs.open(
        path.join(path.abspath(path.dirname(__file__)), 'README.rst'),
        mode='r',
        encoding='utf-8'
    ).read(),
    author='Kenichi Ohtomi',
    author_email='ohtomi.kenichi@gmail.com',
    url='https://github.com/ohtomi/aws-vapor/',
    download_url='https://github.com/ohtomi/aws-vapor/tarball/v0.0.2',
    keywords='aws cloudformation template generator',
    packages=find_packages(),
    install_requires=[
        'cliff',
    ],
    entry_points={
        'console_scripts':
            'aws-vapor = aws_vapor.main:main',
        'aws_vapor.command': [
            'config = aws_vapor.configure:Configure',
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
    ],
)
