import http from 'http';
import axios from 'axios';
import { afterAll, beforeAll, beforeEach, describe, expect, it, jest } from '@jest/globals';
import app from '../server.js';
import Decision from '../models/Decision.js';
import { createToken } from '../middleware/auth.js';

describe('Decisions API', () => {
  let server;
  let baseUrl;
  const token = `Bearer ${createToken({ email: 'demo@symbios.ai' })}`;

  beforeAll((done) => {
    server = http.createServer(app);
    server.listen(0, () => {
      const { port } = server.address();
      baseUrl = `http://127.0.0.1:${port}`;
      done();
    });
  });

  afterAll((done) => {
    server.close(done);
  });

  beforeEach(() => {
    jest.restoreAllMocks();
    jest.clearAllMocks();
  });

  it('rejects requests without auth header', async () => {
    const res = await fetch(`${baseUrl}/api/decisions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payload: {} }),
    });

    expect(res.status).toBe(401);
    const body = await res.json();
    expect(body.error).toBeDefined();
  });

  it('creates a decision with AI calibration response', async () => {
    jest.spyOn(axios, 'post').mockResolvedValue({ data: { omega_score: 0.9, recommendation: 'ACCELERATE' } });
    jest.spyOn(Decision, 'create').mockResolvedValue({
      userId: 'demo@symbios.ai',
      omegaScore: 0.9,
      recommendation: 'ACCELERATE',
      payload: { demo: true },
    });

    const res = await fetch(`${baseUrl}/api/decisions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: token,
      },
      body: JSON.stringify({ payload: { demo: true } }),
    });

    expect(res.status).toBe(201);
    expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/calibrate', { payload: { demo: true } });
    const body = await res.json();
    expect(body.decision.recommendation).toBe('ACCELERATE');
  });

  it('returns recent decisions for the authenticated user', async () => {
    jest.spyOn(Decision, 'find').mockReturnValue({
      sort: () => ({
        limit: () => ({
          lean: () => Promise.resolve([{ omegaScore: 0.4, recommendation: 'MONITOR' }]),
        }),
      }),
    });

    const res = await fetch(`${baseUrl}/api/decisions`, {
      headers: { Authorization: token },
    });

    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.decisions).toHaveLength(1);
    expect(body.decisions[0].recommendation).toBe('MONITOR');
  });
});
