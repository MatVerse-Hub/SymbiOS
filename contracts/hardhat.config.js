require('dotenv').config();
const { POLYGON_RPC_URL, POLYGON_PRIVATE_KEY } = process.env;

module.exports = {
  solidity: '0.8.20',
  networks: {
    hardhat: {},
    amoy: {
      url: POLYGON_RPC_URL || '',
      accounts: POLYGON_PRIVATE_KEY ? [POLYGON_PRIVATE_KEY] : [],
    },
  },
};
