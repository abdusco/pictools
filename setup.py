from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.readlines()

setup(
    name='pictools',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    entry_points='''
        [console_scripts]
        pictools=pictools.cli:cli
    ''',
)
