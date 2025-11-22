import mongoose from 'mongoose';

const decisionSchema = new mongoose.Schema(
  {
    userId: { type: String, required: true },
    omegaScore: { type: Number, required: true },
    recommendation: {
      type: String,
      enum: ['ACCELERATE', 'MONITOR', 'PAUSE'],
      required: true,
    },
    payload: { type: Object, default: {} },
    blockchainTx: { type: String },
  },
  { timestamps: true, collection: 'decisions' }
);

export default mongoose.models.Decision || mongoose.model('Decision', decisionSchema);
