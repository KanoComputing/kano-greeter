#!/usr/bin/env python

from distutils.core import setup
import setuptools

setup(name='Kano Greeter',
      version='1.0',
      description='A greeter for Kano OS',
      author='Team Kano',
      author_email='dev@kano.me',
      url='https://github.com/KanoComputing/kano-greeter',
      packages=['kano_greeter'],
      scripts=['bin/kano-greeter'],
      package_data={'kano_greeter': setuptools.findall('media/css')},
      data_files=[
          ('/usr/share/kano-greeter', setuptools.findall('media/wallpapers')),
          ('/usr/share/xgreeters', ['config/kano-greeter.desktop']),
          ('/var/lib/lightdm', ['config/.kdeskrc'])
      ]
     )
