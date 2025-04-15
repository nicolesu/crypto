// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * Battle the Fearsome Ogre... if you dare!
 */
contract EthermonLite {
    struct Monster {
        uint weight;
        uint wins;
        uint losses;
        string name;
        string nameTitle;
        bool created;
    }

    mapping(address => Monster) public monsters;
    address public Ogre;

    event BattleResult(address challenger, bool challengerWins);
    event MonsterCreated(string monsterName, address owner);

    constructor() {
        Ogre = address(0xfeed);
        monsters[Ogre].wins = 0;
        monsters[Ogre].losses = 0;
        monsters[Ogre].weight = 64;
        monsters[Ogre].name = "Fearsome Ogre";
        monsters[Ogre].nameTitle = "Guru";
        monsters[Ogre].created = true;
    }

    /**
     * Initializes a monster
     * @param _monsterNamePrefix The monster's name
     */
    function initMonster(string memory _monsterNamePrefix) public {
        require(!monsters[msg.sender].created, "Monster already created");
        monsters[msg.sender].wins = 0;
        monsters[msg.sender].losses = 0;
        monsters[msg.sender].weight = 1;
        monsters[msg.sender].name = _monsterNamePrefix;
        monsters[msg.sender].nameTitle = "Newbie";
        monsters[msg.sender].created = true;
        emit MonsterCreated(getName(msg.sender), msg.sender);
    }

    /**
     * Renames your challenger's title
     * @param _newTitle New title for your challenger
     */
    function renameTitle(string calldata _newTitle) public {
        monsters[msg.sender].nameTitle = _newTitle;
    }

    /**
     * @return The full name of your challenger in "name title" format
     */
    function getFullName(address _monsterAddress) public view returns (string memory) {
        return string.concat(monsters[_monsterAddress].name, " ", monsters[_monsterAddress].nameTitle);
    }

    function getName(address _monsterAddress) public view returns (string memory) {
        return monsters[_monsterAddress].name;
    }

    function getNumWins(address _monsterAddress) public view returns (uint) {
        return monsters[_monsterAddress].wins;
    }

    function getNumLosses(address _monsterAddress) public view returns (uint) {
        return monsters[_monsterAddress].losses;
    }

    /**
     * Battles the sender (the challenger) against the Ogre.
     * @return True if the challenger won the battle, false if the Ogre won
     */
    function battle() public returns (bool) {
        address challenger = msg.sender;
        require(
            monsters[challenger].created && monsters[Ogre].created,
            "Challenger not created. Did you call initMonster?"
        );
        uint battleRatio = monsters[Ogre].weight / monsters[challenger].weight;

        // XOR the previous block hash with the hash of the challenger's full name
        uint dice = uint(blockhash(block.number - 1));
        uint challengerDice = dice ^ uint(sha256(bytes(getFullName(challenger))));

        // Challenger wins only if challengerDice mod battleRatio == 0
        bool challengerWins = false;
        if (challengerDice % battleRatio == 0) {
            monsters[challenger].wins += 1;
            monsters[Ogre].losses += 1;
            challengerWins = true;
        } else {
            monsters[challenger].losses += 1;
            monsters[Ogre].wins += 1;
        }
        emit BattleResult(challenger, challengerWins);
        return challengerWins;
    }
}
