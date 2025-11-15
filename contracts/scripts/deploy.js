const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying SymbiOS contracts to Polygon Amoy...");
  
  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log(`📝 Deploying from: ${deployer.address}`);
  
  // Deploy EvidenceNote
  const EvidenceNote = await hre.ethers.getContractFactory("EvidenceNote");
  const evidence = await EvidenceNote.deploy();
  await evidence.deployed();
  console.log(`✅ EvidenceNote deployed to: ${evidence.address}`);
  
  // Deploy OmegaGate
  const OmegaGate = await hre.ethers.getContractFactory("OmegaGate");
  const gate = await OmegaGate.deploy();
  await gate.deployed();
  console.log(`✅ OmegaGate deployed to: ${gate.address}`);
  
  // Save addresses
  const addresses = {
    evidenceNote: evidence.address,
    omegaGate: gate.address,
    deployer: deployer.address,
    timestamp: new Date().toISOString()
  };
  
  console.log("\n📋 Deployment Summary:");
  console.log(JSON.stringify(addresses, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
