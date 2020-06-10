from setuptools import setup

setup(
    name='settable_generator',
    version='0.1',
    packages=['tests', 'settable_generator'],
    package_data={'settable_generator': ['py.typed']},
    url='https://github.com/markusschmaus/settable_generator',
    license='MIT',
    author='Markus Schmaus',
    author_email='markus.schmaus@web.de',
    description='Allow python generators to receive values in for loops.',
    zip_safe=False,
)
