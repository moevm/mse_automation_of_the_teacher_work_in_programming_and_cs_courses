# License MIT

import os
from setuptools import setup, find_packages

DISTRO_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


def extract_requiremens(file):
    """
    Extracts requirements from file
    :param file: path to file
    :return: list[str] -- list of requirements
    """

    with open(file, 'r') as file:
        return file.read().splitlines()


setup(
    name='automation-of-work-for-stepic-distro',
    version='0.1',
    description='Allows you to see statistics on students and courses on stepic.org',
    author='Olga Nosova,',
    author_imail='olenka-nosova@mail.ru',
    license='MIT',
    classifiers=[
        'Topic :: Education'
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=extract_requiremens(os.path.join(DISTRO_ROOT_PATH, 'requirements', 'base.txt')),
    test_requires=extract_requiremens(os.path.join(DISTRO_ROOT_PATH, 'requirements', 'test.txt')),
    scripts=[os.path.join('bin', 'run_application'),os.path.join('bin', 'run.bat'),os.path.join('bin', 'run.sh')],
    include_package_data=True,
    zip_safe=False
)