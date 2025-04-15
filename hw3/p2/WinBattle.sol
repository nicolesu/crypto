// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IEthermonLite {
    function initMonster(string memory _monsterName) external;
    function getName(address _monsterAddress) external view returns (string memory);
    function getFullName(address _monsterAddress) external view returns (string memory);
    function getNumWins(address _monsterAddress) external view returns (uint);
    function getNumLosses(address _monsterAddress) external view returns (uint);
    function battle() external returns (bool);
    function renameTitle(string calldata _newTitle) external;
}

/**
 * This includes a function you might find useful! You can run this by, for example, calling
 * `StringTools.makeString(32);`
 */
library StringTools {
    /**
     * Turns a uint256 number into a string representing the number. This
     * function might be useful to you if you plan to change the challenger
     * name. It's NOT necessary to use this to win.
     * @param number Number to convert to a string.
     * @return string form of the number
     */
    function makeString(uint256 number) internal pure returns (string memory) {
        if (number == 0) {
            return "0";
        }
        uint strLen = 0;
        uint x = number;
        while (x > 0) {
            x /= 10;
            strLen++;
        }
        bytes memory strBytes = new bytes(strLen);
        x = number;
        for (uint i = 0; i < strLen; i++) {
            strBytes[strLen - i - 1] = bytes1(uint8(48 + (x % 10)));
            x /= 10;
        }
        return string(strBytes);
    }
}

contract WinBattle {
    // TODO: Implement this contract for problem 2.

    using StringTools for uint256;
    
    struct BattleState {
        uint256 attemptCount;
        string monsterName;
        bool hasWon;
    }
    
    address private constant ETHERMON = 0xcf2c406f58f9961D468738d8975B16936EE71CE7;
    IEthermonLite private immutable game;
    BattleState private state;
    
    event BattleAttempt(uint256 attempt, bool success);
    
    constructor() {
        game = IEthermonLite(ETHERMON);
        state = BattleState({
            attemptCount: 0,
            monsterName: "warrior",
            hasWon: false
        });
        game.initMonster(state.monsterName);
    }
    
    function _computeBattleValue() private view returns (uint256) {
        bytes32 prevBlock = blockhash(block.number - 1);
        bytes32 nameHash = sha256(bytes(game.getFullName(address(this))));
        return uint256(prevBlock) ^ uint256(nameHash);
    }
    
    function _tryBattle() private returns (bool) {
        uint256 battleValue = _computeBattleValue();
        if (battleValue % 64 == 0) {
            game.battle();
            return true;
        }
        return false;
    }
    
    function _attemptVictory(uint256 maxAttempts) private {
        for (uint256 i = 0; i < maxAttempts && !state.hasWon; i++) {
            game.renameTitle(StringTools.makeString(state.attemptCount));
            state.attemptCount++;
            
            if (_tryBattle()) {
                state.hasWon = true;
                emit BattleAttempt(i, true);
                
                // Win multiple battles once we find a winning combination
                for (uint256 j = 0; j < 50; j++) {
                    game.battle();
                }
                break;
            }
            emit BattleAttempt(i, false);
        }
    }
    
    function winBattle(uint256 maxAttempts) external {
        if (!state.hasWon) {
            _attemptVictory(maxAttempts);
        }
    }
    
    function getBattleStats() external view returns (uint256 attempts, bool hasWon) {
        return (state.attemptCount, state.hasWon);
    }
}
