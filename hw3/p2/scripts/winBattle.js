const hre = require("hardhat");

async function main() {
  // Deploy WinBattle contract
  const WinBattle = await hre.ethers.getContractFactory("WinBattle");
  const winBattle = await WinBattle.deploy();
  await winBattle.deployed();
  console.log("WinBattle deployed to:", winBattle.address);

  // Call winBattle with 10 attempts
  console.log("Calling winBattle...");
  const tx = await winBattle.winBattle(10);
  await tx.wait();
  console.log("Battle completed!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 