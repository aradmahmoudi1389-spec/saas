import type { FastifyReply, FastifyRequest } from 'fastify'
import { getSession, verifyAccessToken } from '../services/authService.js'

declare module 'fastify' { interface FastifyRequest { user?: { id: string; role: string } } }

export async function requireAuth(request: FastifyRequest, reply: FastifyReply) {
  const bearer = request.headers.authorization?.match(/^Bearer\s+(.+)$/i)?.[1]
  if (bearer) {
    try {
      const verified = await verifyAccessToken(bearer)
      const userId = verified.payload.sub
      const role = verified.payload.role
      if (userId && typeof role === 'string') {
        request.user = { id: userId, role }
        return
      }
    } catch {
      return reply.code(401).send({ ok: false, error: { code: 'SESSION_EXPIRED', message: 'نشست شما منقضی شده است.' } })
    }
  }
  const token = request.cookies?.session
  if (!token) return reply.code(401).send({ ok: false, error: { code: 'UNAUTHENTICATED', message: 'ورود لازم است.' } })
  const session = await getSession(token)
  if (!session || session.expiresAt < new Date()) return reply.code(401).send({ ok: false, error: { code: 'SESSION_EXPIRED', message: 'نشست شما منقضی شده است.' } })
  request.user = { id: session.user.id, role: session.user.role }
}

export function requireRole(...roles: string[]) {
  return async (request: FastifyRequest, reply: FastifyReply) => {
    if (!request.user || !roles.includes(request.user.role)) return reply.code(403).send({ ok: false, error: { code: 'FORBIDDEN', message: 'دسترسی کافی ندارید.' } })
  }
}
