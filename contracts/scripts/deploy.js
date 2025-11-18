const fs = require('fs');
const path = require('path');
const { ethers } = require('hardhat');

async function main() {
  const SymbiOS = await ethers.getContractFactory('SymbiOS');
  const contract = await SymbiOS.deploy('deployed');
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  const output = `SymbiOS deployed at ${address}`;
  const outPath = path.join(__dirname, '..', 'deploy-output.txt');
  fs.writeFileSync(outPath, output, 'utf8');
  console.log(output);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
