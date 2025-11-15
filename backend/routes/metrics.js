import express from 'express';
import User from '../models/User.js';
import Decision from '../models/Decision.js';

const router = express.Router();

// GET: User's Ω-Score dashboard
router.get('/omega', async (req, res) => {
  try {
    const user = await User.findById(req.user.userId);
    const decisions = await Decision.find({ user_id: req.user.userId });

    const omega_avg = decisions.length > 0
      ? (decisions.reduce((sum, d) => sum + (d.omega_score || 0), 0) / decisions.length).toFixed(4)
      : 0;

    const recommendations = {
      ACCELERATE: decisions.filter(d => d.recommendation === 'ACCELERATE').length,
      MONITOR: decisions.filter(d => d.recommendation === 'MONITOR').length,
      PAUSE: decisions.filter(d => d.recommendation === 'PAUSE').length
    };

    res.json({
      user_omega_score: user.omega_score,
      decisions_omega_avg: parseFloat(omega_avg),
      decisions_count: decisions.length,
      recommendations,
      antifragile: parseFloat(omega_avg) > 0.85 ? '✅ Yes' : '⚠️ Borderline'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET: Historical metrics (for charts)
router.get('/history', async (req, res) => {
  try {
    const decisions = await Decision.find({ user_id: req.user.userId })
      .sort({ created_at: 1 })
      .limit(30);

    const history = decisions.map(d => ({
      date: d.created_at.toISOString().split('T')[0],
      omega_score: d.omega_score,
      cvar_95: d.cvar_95
    }));

    res.json({ history });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
