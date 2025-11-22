import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import mongoose from 'mongoose';

import authRouter from './routes/auth.js';
import decisionsRouter from './routes/decisions.js';
import { authMiddleware } from './middleware/auth.js';

dotenv.config();

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/auth', authRouter);
app.use('/api/decisions', authMiddleware, decisionsRouter);

const { MONGODB_URI, PORT = 3000 } = process.env;

async function connectDatabase() {
  if (!MONGODB_URI) {
    console.warn('MONGODB_URI not set, skipping database connection.');
    return;
  }

  await mongoose.connect(MONGODB_URI, {
    serverSelectionTimeoutMS: 5000,
  });
  console.info('Connected to MongoDB');
}

if (process.env.NODE_ENV !== 'test') {
  connectDatabase().catch((err) => {
    console.error('Mongo connection failed', err);
  });

  app.listen(PORT, () => {
    console.log(`SymbiOS backend running on port ${PORT}`);
  });
}

export default app;
