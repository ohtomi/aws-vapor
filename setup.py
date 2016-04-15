from setuptools import setup, find_packages

setup(
    name='aws-cfn-gen',
    version='1.0',
    packages=find_packages(),
    install_requires=['cliff'],
    entry_points={
        'console_scripts':
            'aws-cfn-gen = aws_cfn_gen.main:main',
        'aws_cfn_gen.command': [
            'configure = aws_cfn_gen.configure:Configure',
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
