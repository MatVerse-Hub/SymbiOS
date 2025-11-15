const hre = require('hardhat');
const { expect } = require('chai');

describe('EvidenceNote Contract', () => {
  let evidenceNote;
  let owner, addr1;

  beforeEach(async () => {
    [owner, addr1] = await hre.ethers.getSigners();
    const EvidenceNote = await hre.ethers.getContractFactory('EvidenceNote');
    evidenceNote = await EvidenceNote.deploy();
    await evidenceNote.deployed();
  });

  it('Should mint evidence note', async () => {
    const tx = await evidenceNote.mint_evidence(
      'Market Launch Decision',
      8700, // Ω-Score scaled to 0-10000
      150,  // CVaR-95 scaled
      '0x' + '0'.repeat(64)
    );

    const receipt = await tx.wait();
    expect(receipt.status).to.equal(1);
  });

  it('Should retrieve evidence', async () => {
    await evidenceNote.mint_evidence(
      'Test Decision',
      8700,
      150,
      '0x' + '0'.repeat(64)
    );

    const evidence = await evidenceNote.get_evidence(0);
    expect(evidence.decision_title).to.equal('Test Decision');
  });

  it('Should identify antifragile evidence', async () => {
    await evidenceNote.mint_evidence(
      'Antifragile Decision',
      8800, // Ω > 0.85
      150,
      '0x' + '0'.repeat(64)
    );

    const isAntifragile = await evidenceNote.is_antifragile(0);
    expect(isAntifragile).to.be.true;
  });
});

describe('OmegaGate Contract', () => {
  let omegaGate;

  beforeEach(async () => {
    const OmegaGate = await hre.ethers.getContractFactory('OmegaGate');
    omegaGate = await OmegaGate.deploy();
    await omegaGate.deployed();
  });

  it('Should recommend ACCELERATE', async () => {
    const decision = await omegaGate.evaluate(8700, 15);
    expect(decision).to.equal(0); // ACCELERATE = 0
  });

  it('Should recommend MONITOR', async () => {
    const decision = await omegaGate.evaluate(6800, 70);
    expect(decision).to.equal(1); // MONITOR = 1
  });

  it('Should recommend PAUSE', async () => {
    const decision = await omegaGate.evaluate(5000, 120);
    expect(decision).to.equal(2); // PAUSE = 2
  });
});
