from setuptools import setup, find_packages

setup(
    name='evm-cfg-builder',
    description='EVM cfg builder written in Python 3.',
    url='https://github.com/trailofbits/evm_cfg_builder',
    author='Trail of Bits',
    version='0.1.0',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['pyevmasm>=0.1.1'],
    license='AGPL-3.0',
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': [
            'evm-cfg-builder = evm_cfg_builder.__main__:main'
        ]
    }
)
