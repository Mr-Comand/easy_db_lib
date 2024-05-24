# setup.py
from setuptools import setup, find_packages

setup(
    name='easy_db_lib',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
       'psycopg2==2.9.9',
    ],
    entry_points={
        'console_scripts': [
            # Define any command-line scripts here
        ],
    },
    author='Mr_comand',
    description='A very simple db lib.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/mr-comand/easy_db_lib',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
