from setuptools import setup, find_packages

with open('README.md', encoding="utf-8") as file_readme:
    long_description = file_readme.read()

setup(
    name='evm-cfg-builder',
    description='EVM cfg builder written in Python 3.',
    url='https://github.com/trailofbits/evm_cfg_builder',
    author='Trail of Bits',
    version='0.3.1',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['pyevmasm>=0.1.1', 'crytic-compile>=0.1.13'],
    license='AGPL-3.0',
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'evm-cfg-builder = evm_cfg_builder.__main__:main'
        ]
    }
)
