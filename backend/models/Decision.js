import mongoose from 'mongoose';

const decisionSchema = new mongoose.Schema({
  user_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  title: String,
  context: String,
  human_confidence: {
    type: Number,
    min: 0,
    max: 1
  },
  risk_tolerance: {
    type: Number,
    min: 0,
    max: 1
  },
  omega_score: {
    type: Number,
    min: 0,
    max: 1
  },
  cvar_95: {
    type: Number,
    min: 0,
    max: 1
  },
  recommendation: {
    type: String,
    enum: ['ACCELERATE', 'MONITOR', 'PAUSE'],
    default: 'MONITOR'
  },
  blockchain_proof: String, // ERC-721 token address
  blockchain_tx: String,    // Transaction hash on Polygon
  status: {
    type: String,
    enum: ['pending', 'processing', 'completed', 'failed'],
    default: 'pending'
  },
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
}, { collection: 'decisions' });

export default mongoose.model('Decision', decisionSchema);
