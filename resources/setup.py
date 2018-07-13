import os
from setuptools import setup

setup(
    name='gaukl.resources',
    version='0.8.0',
    url='',
    license='Mozilla Public License 2.0 (MPL 2.0)',
    author='Vincent Barth',
    author_email='vdbarth@posteo.at',
    description='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)'
    ],
    packages=['gaukl', 'gaukl.resources'],
    package_dir={'': 'src'},
    namespace_packages=['gaukl'],
    package_data={'gaukl': [dir.replace('src/gaukl', '') for dir, _, _ in os.walk('src/gaukl/resources')]},
    include_package_data=True
)