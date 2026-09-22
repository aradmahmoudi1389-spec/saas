import { z } from 'zod'
import type { FastifyInstance } from 'fastify'
import { prisma } from '../../db/client.js'
import { createAccessToken, createSession, hashPassword, revokeSession, verifyPassword } from '../../services/authService.js'

const registerSchema = z.object({ phone: z.string().regex(/^09\d{9}$/), password: z.string().min(8), firstName: z.string().min(1).max(80) })
const loginSchema = z.object({ phone: z.string().regex(/^09\d{9}$/), password: z.string().min(1) })

export async function authRoutes(app: FastifyInstance) {
  app.post('/register', async (request, reply) => {
    const input = registerSchema.parse(request.body)
    const exists = await prisma.user.findUnique({ where: { phone: input.phone } })
    if (exists) return reply.code(409).send({ ok: false, error: { code: 'PHONE_EXISTS', message: 'این شماره قبلاً ثبت شده است.' } })
    const user = await prisma.user.create({ data: { phone: input.phone, firstName: input.firstName, passwordHash: await hashPassword(input.password), profile: { create: {} } } })
    const session = await createSession(user.id)
    reply.setCookie('session', session.token, { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'lax', expires: session.expiresAt, path: '/' })
    return reply.code(201).send({ ok: true, data: { user: { id: user.id, phone: user.phone, firstName: user.firstName }, accessToken: await createAccessToken(user.id, user.role) } })
  })
  app.post('/login', async (request, reply) => {
    const input = loginSchema.parse(request.body)
    const user = await prisma.user.findUnique({ where: { phone: input.phone } })
    if (!user?.passwordHash || !(await verifyPassword(user.passwordHash, input.password))) return reply.code(401).send({ ok: false, error: { code: 'INVALID_CREDENTIALS', message: 'شماره یا رمز عبور نادرست است.' } })
    const session = await createSession(user.id)
    reply.setCookie('session', session.token, { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'lax', expires: session.expiresAt, path: '/' })
    return { ok: true, data: { user: { id: user.id, phone: user.phone, firstName: user.firstName }, accessToken: await createAccessToken(user.id, user.role) } }
  })
  app.post('/logout', async (request, reply) => { const token = request.cookies?.session; if (token) await revokeSession(token); reply.clearCookie('session', { path: '/' }); return { ok: true, data: null } })
}
