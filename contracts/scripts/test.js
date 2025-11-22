const assert = require('assert');
const fs = require('fs');
const path = require('path');

const contractPath = path.join(__dirname, '..', 'contracts', 'SymbiOS.sol');
const src = fs.readFileSync(contractPath, 'utf8');

assert(src.includes('contract SymbiOS'), 'Contract definition missing');
assert(src.includes('setMessage'), 'setMessage function missing');
assert(src.includes('getMessage'), 'getMessage function missing');

console.log('contracts test: static assertions passed');
