import express from 'express';
import axios from 'axios';
import dotenv from 'dotenv';
import Decision from '../models/Decision.js';

dotenv.config();

const router = express.Router();
const { AI_SERVICE_URL = 'http://localhost:8000' } = process.env;

router.post('/', async (req, res) => {
  const { payload = {} } = req.body;
  const userId = req.user?.email || 'anonymous';

  try {
    const aiResponse = await axios.post(`${AI_SERVICE_URL}/calibrate`, { payload });
    const { omega_score: omegaScore, recommendation } = aiResponse.data;

    const record = await Decision.create({
      userId,
      payload,
      omegaScore,
      recommendation,
    });

    return res.status(201).json({ decision: record });
  } catch (err) {
    console.error('Decision pipeline failed', err.message);
    return res.status(502).json({ error: 'Decision pipeline failed' });
  }
});

router.get('/', async (req, res) => {
  const decisions = await Decision.find({ userId: req.user?.email || 'anonymous' })
    .sort({ createdAt: -1 })
    .limit(20)
    .lean();
  return res.json({ decisions });
});

export default router;
