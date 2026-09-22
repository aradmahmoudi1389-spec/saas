import { createHash, randomBytes } from 'node:crypto'
import argon2 from 'argon2'
import { SignJWT, jwtVerify } from 'jose'
import { env } from '../config/env.js'
import { prisma } from '../db/client.js'

const secret = new TextEncoder().encode(env.JWT_SECRET)
const SESSION_DAYS = 30

export async function hashPassword(password: string) { return argon2.hash(password) }
export async function verifyPassword(hash: string, password: string) { return argon2.verify(hash, password) }
export async function createSession(userId: string) {
  const token = randomBytes(48).toString('base64url')
  const tokenHash = createHash('sha256').update(token).digest('hex')
  const expiresAt = new Date(Date.now() + SESSION_DAYS * 86400000)
  await prisma.session.create({ data: { userId, tokenHash, expiresAt } })
  return { token, expiresAt }
}
export async function getSession(token: string) {
  const tokenHash = createHash('sha256').update(token).digest('hex')
  return prisma.session.findUnique({ where: { tokenHash }, include: { user: true } })
}
export async function revokeSession(token: string) {
  const tokenHash = createHash('sha256').update(token).digest('hex')
  await prisma.session.deleteMany({ where: { tokenHash } })
}
export async function createAccessToken(userId: string, role: string) {
  return new SignJWT({ role }).setProtectedHeader({ alg: 'HS256' }).setSubject(userId).setIssuedAt().setExpirationTime('15m').sign(secret)
}
export async function verifyAccessToken(token: string) {
  return jwtVerify(token, secret)
}
