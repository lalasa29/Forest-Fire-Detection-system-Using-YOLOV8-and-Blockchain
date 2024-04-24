// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FireDetection {
    // Structure to hold fire detection details
    struct FireEvent {
        string time; 
        uint8 day;
        uint8 month;
        uint16 year;
    }

    // Mapping to store fire detection events
    mapping(uint => FireEvent) public fireEvents;

    // Event emitted when fire is detected
    event FireDetected(uint indexed eventId, string time, uint8 day, uint8 month, uint16 year);

    // Function to add a new fire detection event
    function addFireEvent(string memory time, uint8 day, uint8 month, uint16 year) external {
        uint eventId = uint(keccak256(abi.encodePacked(time, day, month, year)));
        fireEvents[eventId] = FireEvent(time, day, month, year);
        emit FireDetected(eventId, time, day, month, year);
    }
}