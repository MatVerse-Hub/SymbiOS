{
  "testEnvironment": "node",
  "testMatch": ["**/__tests__/**/*.js", "**/?(*.)+(spec|test).js"],
  "collectCoverageFrom": [
    "backend/**/*.js",
    "!backend/node_modules/**",
    "!backend/server.js"
  ],
  "coverageThreshold": {
    "global": {
      "branches": 80,
      "functions": 80,
      "lines": 80
    }
  }
}
