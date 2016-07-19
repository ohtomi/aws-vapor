from setuptools import setup, find_packages

setup(
    name='aws-vapor',
    version='0.0.1',
    packages=find_packages(),
    install_requires=['cliff'],
    entry_points={
        'console_scripts':
            'aws-vapor = aws_vapor.main:main',
        'aws_vapor.command': [
            'config = aws_vapor.configure:Configure',
            'template = aws_vapor.generator:Generator',
        ]
    },
    zip_safe=False,
    classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
    ],
)
