
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
        'biopython>=1.63',
        'bottle>=0.10',
        'doit==0.25.0'
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha"
    ],
    entry_points= {
        'distutils.commands': [
            'web_setup = web_cms.local_setup:LocalSetupCommand'
        ],

        'console_scripts': [
            'email-validate    = mibc.email.cli:main',
            'assembly          = mibc.assembly:main',
            'mibc_build        = mibc.automated.cli:main',
            'mibc_convert      = mibc.utility_scripts.convert:main',
            'mibc_fastq_split  = mibc.utility_scripts.seqsplit:main',
            'mibc_map_writer   = mibc.utility_scripts.mapwrite:main',
            'mibc_web_worker   = mibc.web:main',
        ],
    }
)
