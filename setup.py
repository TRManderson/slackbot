"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = []
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        before, *after = line.split('#', 1)
        data = before.strip()
        if data:
            install_requires.append(data)

setup(
    name='slackbot',
    version='0.0.1',
    description='A lightweight slack bot framework',
    long_description=long_description,
    url='https://github.com/TRManderson/slackbot',
    author='Tom Manderson',
    author_email='me@trm.io',
    license='BSD3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD3 License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='slack async lightweight',
    packages=find_packages(),
    install_requires=install_requires,

)