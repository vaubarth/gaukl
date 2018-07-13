from setuptools import setup

setup(
    name='gaukl.juggler',
    version='0.1.0',
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
    packages=['gaukl','gaukl.juggler'],
    package_dir={'': 'src'},
    namespace_packages=['gaukl'],
    install_requires=[
        'gaukl.core',
        'gaukl.resources',
        'flask',
        'requests'
    ],

)
