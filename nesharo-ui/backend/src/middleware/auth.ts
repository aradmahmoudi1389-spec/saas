import type { FastifyReply, FastifyRequest } from 'fastify'
import { getSession } from '../services/authService.js'

declare module 'fastify' { interface FastifyRequest { user?: { id: string; role: string } } }

export async function requireAuth(request: FastifyRequest, reply: FastifyReply) {
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
