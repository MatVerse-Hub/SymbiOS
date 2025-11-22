import jwt from 'jwt-simple';
import dotenv from 'dotenv';

dotenv.config();

const resolvedSecret = process.env.JWT_SECRET || (process.env.NODE_ENV === 'test' ? 'test-secret' : null);

if (!resolvedSecret) {
  throw new Error('JWT_SECRET must be set before starting the backend');
}

export function authMiddleware(req, res, next) {
  const header = req.headers.authorization;
  if (!header) {
    return res.status(401).json({ error: 'Missing Authorization header' });
  }

  const [scheme, token] = header.split(' ');
  if (scheme !== 'Bearer' || !token) {
    return res.status(401).json({ error: 'Invalid Authorization format' });
  }

  try {
    const decoded = jwt.decode(token, resolvedSecret);
    req.user = decoded;
    return next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}

export function createToken(payload) {
  return jwt.encode(payload, resolvedSecret);
}
