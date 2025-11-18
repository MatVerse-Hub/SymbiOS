import express from 'express';
import dotenv from 'dotenv';
import { createToken } from '../middleware/auth.js';

dotenv.config();

const router = express.Router();
const { DEFAULT_EMAIL = 'demo@symbios.ai', DEFAULT_PASSWORD = 'password' } = process.env;

router.post('/login', (req, res) => {
  const { email, password } = req.body;

  if (email !== DEFAULT_EMAIL || password !== DEFAULT_PASSWORD) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const token = createToken({ email });
  return res.json({ token });
});

router.post('/register', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' });
  }

  // Placeholder registration logic
  return res.status(201).json({ email, message: 'User registered (demo only)' });
});

export default router;
