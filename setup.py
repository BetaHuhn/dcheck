from setuptools import setup
setup(
    name='dcheck',
    version='1.0',
    description='Mass Domain Availability Checker',
    author='Maximilian Schiller',
    author_email='schiller@mxis.ch',
    packages=['dcheck'],
    entry_points={
        'console_scripts' : ['dcheck=dcheck.check:main'],
    },
    install_requires=[
        'requests',
        'termcolor',
    ]
)