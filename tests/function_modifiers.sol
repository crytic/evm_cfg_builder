//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "hardhat/console.sol";

contract Something {
    address public owner;
    uint blockNumber = 1337;
    constructor() {
        owner = msg.sender;
    }

    function a() public view returns (uint) {
        return 1;
    }

    function b() public pure returns (uint) {
        return 2;
    }

    function c() external pure returns (uint) {
        return 3;
    }

    function d() internal pure returns (uint) {
        return 4;
    }

    function e() private pure returns (uint) {
        return 5;
    }

    function f() internal returns (uint) {
        return 6;
    }

    function z() public payable returns (uint) {
        d();
        e();
        return 6;
    }
}
