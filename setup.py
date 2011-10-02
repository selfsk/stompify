from setuptools import setup, find_packages
import os
import sys

if os.path.exists('src'):
    sys.path.insert(0, 'src')

#from f9 import version

setup(
    name = "stompify",
    version = "0.1",
    packages = find_packages('src'),
    package_dir = {'': 'src'},
 
    package_data = {'': ['']},
    zip_safe = True,  
    author = "Sergei Kononov",
    author_email = "self.sik@gmail.com",
    description = "STOMP protocol in pure twisted",

    install_requires=["twisted"],
    entry_points = {'console_scripts': ['stompify-srv = stompify.scripts:run_simple']

                    },
)
