import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    match: [/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/, 'Invalid email']
  },
  password: {
    type: String,
    required: true,
    minlength: 8
  },
  name: String,
  organization: String,
  risk_tolerance: {
    type: Number,
    default: 0.5,
    min: 0,
    max: 1
  },
  omega_score: {
    type: Number,
    default: 0.85
  },
  decisions_count: {
    type: Number,
    default: 0
  },
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
}, { collection: 'users' });

export default mongoose.model('User', userSchema);
