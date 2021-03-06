from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aisac_iodef2stix',

    version='0.9.0',

    description='AISAC IODEF to STIX',
    long_description=long_description,

    url='https://github.com/cjltsod/aisac-iodef2stix',

    author='CJLTSOD',

    license='MIT',

    classifiers=[
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='aisac iodef stix',
    py_modules=["iodef2stix"],

    install_requires=['pyjnius', 'cython'],
)
