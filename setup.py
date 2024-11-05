from setuptools import setup, find_packages

setup(
    name='fiber photometry analysis',
    version='0.1',
    packages=find_packages(include=['src', 'src.*']),
    url='https://github.com/GergelyTuri/fiberphotometry',
    license='MIT',
    author='Gergely Turi',
    author_email='gt2253@cumc.columbia.edu',
    description='some basic analysis code'
)