from setuptools import setup

setup(
    name='gaukl.core',
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
    packages=['gaukl', 'gaukl.core',
              'gaukl.core.context', 'gaukl.core.helper', 'gaukl.core.store',
              'gaukl.core.api', 'gaukl.core.api.web',
              'gaukl.core.tasks', 'gaukl.core.tasks.general',
              'gaukl.core.tasks.listeners', 'gaukl.core.tasks.transformers', 'gaukl.core.tasks.rules',
              ],
    package_dir={'': 'src'},
    namespace_packages=['gaukl'],
    install_requires=[
        'pyyaml',
        'gevent',
        'flask',
        'jinja2',
        'xmltodict',
        'dpath',
        'requests',
        'tinydb'
    ],

)
