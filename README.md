# EVM CFG BUILDER

`evm_cfg_builder` is used to extract a control flow graph (CFG) from EVM bytecode. It is used by Ethersplay, Manticore, and  other tools from Trail of Bits. It is a reliable foundation to build program analysis tools for EVM.

We encourage contributions that address any known [issues](https://github.com/trailofbits/evm_cfg_builder/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc) and will pay out bounties for accepted PRs. Join us on the [Empire Hacking Slack](https://empireslacking.herokuapp.com) to discuss using or extending evm_cfg_builder.

## Features

* Reliably recovers a Control Flow Graph (CFG) from EVM bytecode
* Recovers attributes (e.g., payable, view, pure)
* Outputs the CFG to a dot file

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
See [examples/library.py](examples/library.py) for an example.

## How to install

```
git clone https://github.com/trailofbits/evm_cfg_builder
pip install .
```

## Requirements

* [pyevmasm](https://github.com/trailofbits/pyevmasm)

## License

evm_cfg_builder is licensed and distributed under the AGPLv3. [Contact us](mailto:opensource@trailofbits.com) if you're looking for an exception to the terms.
