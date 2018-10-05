# EVM CFG BUILDER

Use this library to extract a control flow graph (CFG) from EVM bytecode. `evm_cfg_builder` is used by Ethersplay, Manticore, and many other tools from Trail of Bits.

## Features

evm_cfg_builder is a work in progress, but it's already very useful today:

* Reliably recovers a Control Flow Graph (CFG) from EVM bytecode
* Recovers attributes (e.g., payable, view, pure)
* Outputs the CFG to a dot file

We're looking for help cleaning up the API, adding documentation, improving the VSA, and exporting the dispatcher.

## Example

```
$ python evm_cfg_builder/cfg_builder.py tests/fomo3d.evm
...

dividendsOf(address), 7 #bbs , view
name(), 16 #bbs , view
calculateTokensReceived(uint256), 29 #bbs , view
totalSupply(), 5 #bbs , view
calculateEthereumReceived(uint256), 26 #bbs , view
onlyAmbassadors(), 5 #bbs , view
decimals(), 5 #bbs , view
administrators(bytes32), 5 #bbs , view
withdraw(), 20 #bbs 
sellPrice(), 27 #bbs , view
stakingRequirement(), 5 #bbs , view
myDividends(bool), 13 #bbs , view
totalEthereumBalance(), 5 #bbs , view
balanceOf(address), 5 #bbs , view
setStakingRequirement(uint256), 7 #bbs 
buyPrice(), 30 #bbs , view
setAdministrator(bytes32,bool), 7 #bbs 
Hourglass(), 5 #bbs , view
myTokens(), 7 #bbs , view
symbol(), 16 #bbs , view
disableInitialStage(), 7 #bbs 
transfer(address,uint256), 48 #bbs , view
setSymbol(string), 22 #bbs 
setName(string), 22 #bbs 
sell(uint256), 42 #bbs 
exit(), 63 #bbs 
buy(address), 71 #bbs , payable
reinvest(), 86 #bbs 
```

`test_<name>.dot` files will be generated.

## Requirements

* [pyevmasm](https://github.com/trailofbits/pyevmasm)

## License

evm_cfg_builder is licensed and distributed under the AGPLv3. [Contact us](mailto:opensource@trailofbits.com) if you're looking for an exception to the terms.
