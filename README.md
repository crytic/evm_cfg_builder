# EVM CFG BUILDER
[![Build Status](https://travis-ci.org/crytic/evm_cfg_builder.svg?branch=master)](https://travis-ci.org/crytic/evm_cfg_builder)
[![Slack Status](https://empireslacking.herokuapp.com/badge.svg)](https://empireslacking.herokuapp.com)
[![PyPI version](https://badge.fury.io/py/evm-cfg-builder.svg)](https://badge.fury.io/py/evm-cfg-builder)

`evm-cfg-builder` is used to extract a control flow graph (CFG) from EVM bytecode. It is used by Ethersplay, Manticore, and  other tools from Trail of Bits. It is a reliable foundation to build program analysis tools for EVM.

We encourage contributions that address any known [issues](https://github.com/trailofbits/evm_cfg_builder/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc) and will pay out bounties for accepted PRs. Join us on the [Empire Hacking Slack](https://empireslacking.herokuapp.com) to discuss using or extending `evm-cfg-builder`.

## Features

* Reliably recovers a Control Flow Graph (CFG) from EVM bytecode using a dedicated Value Set Analysis
* Recovers functions names
* Recovers attributes (e.g., payable, view, pure)
* Outputs the CFG to a dot file
* Library API

## Usage

### Command line

To export basic dissassembly information, run:
```
evm-cfg-builder mycontract.evm 
```

To export the CFG of each function (dot format), run:
```
evm-cfg-builder mycontract.evm --export-dot my_dir 
```

dot files can be read using xdot.

### Library
See [examples/explore_cfg.py](examples/explore_cfg.py) and [examples/explore_functions.py](examples/explore_functions.py) for library examples.

## How to install

### Using Pip
```
$ pip install evm-cfg-builder
```

### Using Git
```
git clone https://github.com/trailofbits/evm_cfg_builder
pip install .
```

## Requirements

* Python >= 3.6
* [pyevmasm](https://github.com/trailofbits/pyevmasm)

## Getting Help

Feel free to stop by our [Slack channel](https://empireslacking.herokuapp.com) (#ethereum) for help using or extending evm-cfg-builder.

## License

`evm-cfg-builder` is licensed and distributed under the AGPLv3. [Contact us](mailto:opensource@trailofbits.com) if you're looking for an exception to the terms.
