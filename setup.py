from setuptools import setup, find_packages

setup(name='pictools',
      version='0.0.1',
      description='A collection of image processing and organization tools',
      author='Abdussamet Kocak',
      author_email='abdus@abdus.co',
      packages=['pictools'],
      install_requires=['Pillow', 'click'],
      entry_points={
          'console_scripts': [
              'processimgs = pictools.pictools:cli'
          ]
      }
      )
