const fs = require('fs');
const path = require('path');

const contractPath = path.join(__dirname, '..', 'contracts', 'SymbiOS.sol');
const source = fs.readFileSync(contractPath, 'utf8');

if (!source.includes('SPDX-License-Identifier')) {
  console.error('License header missing');
  process.exit(1);
}
if (!source.includes('pragma solidity')) {
  console.error('Pragma directive missing');
  process.exit(1);
}
console.log('contracts lint: basic headers present');
