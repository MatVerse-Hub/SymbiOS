const { expect } = require('chai');
const { ethers } = require('hardhat');

describe('SymbiOS', () => {
  it('stores and updates a message', async () => {
    const SymbiOS = await ethers.getContractFactory('SymbiOS');
    const contract = await SymbiOS.deploy('hello');
    await contract.waitForDeployment();

    expect(await contract.getMessage()).to.equal('hello');

    const tx = await contract.setMessage('updated');
    await tx.wait();

    expect(await contract.getMessage()).to.equal('updated');
  });
});
