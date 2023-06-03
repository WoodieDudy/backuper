from setuptools import setup, find_packages

setup(
    name='backuper',
    version='0.1.0',
    url='https://github.com/WoodieDudy/backuper',
    author='marga and woodie',
    packages=find_packages(),
    install_requires=['croniter==1.3.8', 'PyDrive==1.3.1', 'yadisk==1.3.2'],
    entry_points={
        'console_scripts': [
            'backuper=backuper.backup:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
    ],
)
