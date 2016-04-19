from setuptools import setup, find_packages

setup(
    name='cfngen',
    version='1.0',
    packages=find_packages(),
    install_requires=['cliff'],
    entry_points={
        'console_scripts':
            'cfngen = cfngen.main:main',
        'cfngen.command': [
            'config = cfngen.configure:Configure',
            'template = cfngen.generator:Generator',
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
