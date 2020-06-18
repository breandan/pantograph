from setuptools import setup

setup(
    name='pantograph',
    version='0.0.1',
    packages=[''],
    url='https://github.com/breandan/pantograph',
    license='',
    author='breandan',
    author_email='bre@ndan.co',
    description='Python computation graph',
    install_requires=[
        'gast',
        'asttokens',
        'pydot',
        'Pillow',
        'numpy',
        'beniget'
    ],
    dependency_links=[
        'http://github.com/serge-sans-paille/beniget/tarball/master#egg=package-1.0'
    ]
)
