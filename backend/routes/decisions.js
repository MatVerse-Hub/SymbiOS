import express from 'express';
import Decision from '../models/Decision.js';
import axios from 'axios';

const router = express.Router();
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8001';

// POST: Create a new decision
router.post('/', async (req, res) => {
  try {
    const { title, context, human_confidence, risk_tolerance } = req.body;
    const userId = req.user.userId;

    // Call AI service for calibration
    const aiResponse = await axios.post(`${AI_SERVICE_URL}/calibrate`, {
      context,
      human_confidence,
      risk_tolerance
    });

    const { omega_score, cvar_95, recommendation } = aiResponse.data;

    // Save decision
    const decision = new Decision({
      user_id: userId,
      title,
      context,
      human_confidence,
      risk_tolerance,
      omega_score,
      cvar_95,
      recommendation,
      status: 'completed'
    });

    await decision.save();

    // TODO: Anchor to blockchain (ERC-721)
    // const blockchainProof = await mintEvidenceNote(decision);
    // decision.blockchain_proof = blockchainProof;
    // await decision.save();

    res.status(201).json({
      id: decision._id,
      omega_score,
      cvar_95,
      recommendation,
      timestamp: decision.created_at
    });
  } catch (error) {
    console.error('Decision creation error:', error);
    res.status(500).json({ error: error.message });
  }
});

// GET: Retrieve decision by ID
router.get('/:id', async (req, res) => {
  try {
    const decision = await Decision.findById(req.params.id);
    if (!decision) {
      return res.status(404).json({ error: 'Decision not found' });
    }
    res.json(decision);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET: List user's decisions with pagination
router.get('/', async (req, res) => {
  try {
    const { page = 1, limit = 10 } = req.query;
    const skip = (page - 1) * limit;

    const decisions = await Decision.find({ user_id: req.user.userId })
      .sort({ created_at: -1 })
      .skip(skip)
      .limit(parseInt(limit));

    const total = await Decision.countDocuments({ user_id: req.user.userId });

    res.json({
      decisions,
      pagination: { page: parseInt(page), limit: parseInt(limit), total }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
