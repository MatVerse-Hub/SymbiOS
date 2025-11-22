// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SymbiOS {
    string private message;

    event MessageUpdated(string newMessage);

    constructor(string memory initialMessage) {
        message = initialMessage;
        emit MessageUpdated(initialMessage);
    }

    function setMessage(string calldata newMessage) external {
        message = newMessage;
        emit MessageUpdated(newMessage);
    }

    function getMessage() external view returns (string memory) {
        return message;
    }
}
