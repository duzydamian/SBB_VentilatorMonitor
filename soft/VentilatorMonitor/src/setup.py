#!/usr/bin/python
#
# Author : Damian Karbowiak
# Company: 
#
# Date   : 13.07.2017
#

##################################################################################################################
# IMPORT LIBRARY
##################################################################################################################
import os
import sys
from setuptools import setup, find_packages

def checkPathAndRemove(path):
    if os.path.exists(path):
        for fileName in os.listdir(path):
            fileNameWithPath = os.path.join(path, fileName)
            os.remove(fileNameWithPath)
            
here = os.path.abspath(os.path.dirname(__file__))
checkPathAndRemove(here+"/dist")
#README = open(os.path.join(here, 'README.txt')).read()
#CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

if "--version" in sys.argv:
    ver = sys.argv.pop(sys.argv.index("--version")+1)
    sys.argv.remove("--version") 
        
requires = [
    'pygatt',    
    'pyexpect',
]

setup(
    name='dk-wm',
    version=ver,
    description='Ventilator Monitor software to run on Raspberry Pi.',
    #long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Damian Karbowiak',
    author_email='',
    url='',
    keywords='ventilator monitor air flow',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
#    console=["run.py"],
)
