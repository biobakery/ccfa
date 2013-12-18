
from setuptools import setup, find_packages

setup(
    name='mibc',
    version='0.0.1',
    description='CCFA data repository and automated analysis service',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    zip_safe=False,
    install_requires=[
        'nose>=1.3.0',
        'python-dateutil>=2.2',
        'six>=1.4.1'
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha"
    ],
    entry_points= {
        'console_scripts': [
            'email-validate = mibc.email.cli:main',
        ],
    }
)
