# setup.py
#!/usr/bin/env python

from distutils.core import setup

setup(name='exchrate' ,
      version='0.1.0' ,
      author='Anton Shestakov' ,
      author_email='anton.shestakov2@gmail.com' ,
      url='https://github.com/anton-shestakov' ,
      packages=['exchrate'] ,
      package_data={'exchrate': ['data/iso_4217.xml']} ,
      scripts=['bin/simple_usage.py'] ,
      install_requires=[
          "grequests"
      ]
     )
