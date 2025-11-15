const request = require('supertest');
const app = require('../backend/server');
const User = require('../backend/models/User');
const jwt = require('jwt-simple');

describe('Authentication Routes', () => {
  let token;
  const testUser = {
    email: 'test@example.com',
    password: 'password123',
    name: 'Test User',
    organization: 'Test Corp'
  };

  beforeAll(async () => {
    // Mock user database
    jest.mock('../backend/models/User');
  });

  test('POST /api/auth/signup - Create new user', async () => {
    const response = await request(app)
      .post('/api/auth/signup')
      .send(testUser);

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('token');
    expect(response.body).toHaveProperty('user');
    token = response.body.token;
  });

  test('POST /api/auth/login - User login', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: testUser.email,
        password: testUser.password
      });

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('token');
  });

  test('POST /api/auth/login - Invalid credentials', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: testUser.email,
        password: 'wrongpassword'
      });

    expect(response.status).toBe(401);
    expect(response.body).toHaveProperty('error');
  });
});
