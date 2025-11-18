import jwt from 'jwt-simple';
import dotenv from 'dotenv';

dotenv.config();

const { JWT_SECRET = 'changeme' } = process.env;

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
    const decoded = jwt.decode(token, JWT_SECRET);
    req.user = decoded;
    return next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}

export function createToken(payload) {
  return jwt.encode(payload, JWT_SECRET);
}
