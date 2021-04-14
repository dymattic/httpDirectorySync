from setuptools import setup

setup(
    name='httpDirectorySync',
    version='v0.1-alpha',
    packages=[
        'PySimpleGUI~=4.39.1',
        'future~=0.18.2',
        'setuptools~=56.0.0',
        'beautifulsoup4~=4.9.3',
        'requests~=2.25.1',
    ],
    url='https://github.com/dymattic/httpDirectorySync',
    license='GNU Affero General Public License v3.0',
    author='dymattic',
    author_email='dymattic@naise.io',
    description='HTTP Directory Sync'
)
