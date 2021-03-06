from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import find_packages, setup


def extract_requirements(filename):
    return [str(r.req) for r in parse_requirements(filename, session=PipSession())]

setup(
    name='qikfiller',
    version='0.1.0-dev',
    packages=find_packages(),
    url='',
    license='MIT',
    author='Josha Inglis',
    author_email='josha.inglis@biarri.com',
    description='Faster way to fill qiktimes timesheets',
    requires=[
        'dateutil',
        'fire',
        'marshmallow',
        'requests',
        'six',
        'SQLAlchemy',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: MIT',
        'Programming Language :: Python',
        'Programming Language :: Python:2.7',
        'Programming Language :: Python:3.3',
        'Programming Language :: Python:3.4',
        'Programming Language :: Python:3.5',
        'Programming Language :: Python:3.6',
    ],
    entry_points={
        'console_scripts': ['qikfiller=qikfiller.cli:main'],
    }
)
