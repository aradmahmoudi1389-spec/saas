import Fastify from 'fastify'
import cookie from '@fastify/cookie'
import cors from '@fastify/cors'
import helmet from '@fastify/helmet'
import rateLimit from '@fastify/rate-limit'
import swagger from '@fastify/swagger'
import swaggerUi from '@fastify/swagger-ui'
import { ZodError } from 'zod'
import { env } from './config/env.js'
import { closeDatabase } from './db/client.js'
import { authRoutes } from './modules/auth/routes.js'
import { brandRoutes } from './modules/brand/routes.js'
import { dashboardRoutes, roadmapRoutes } from './modules/dashboardRoutes.js'
import { requireAuth, requireRole } from './middleware/auth.js'
import { prisma } from './db/client.js'

export function buildApp() {
  const app = Fastify({ logger: env.NODE_ENV !== 'test', trustProxy: true })
  app.register(helmet)
  app.register(cors, { origin: env.FRONTEND_ORIGIN, credentials: true })
  app.register(cookie)
  app.register(rateLimit, { max: 120, timeWindow: '1 minute' })
  app.register(swagger, { openapi: { info: { title: 'Nesharo API', version: '1.0.0' }, servers: [{ url: `http://localhost:${env.PORT}` }] } })
  app.register(swaggerUi, { routePrefix: '/docs' })
  app.get('/health', async () => ({ ok: true, data: { service: 'nesharo-api', status: 'healthy' } }))
  app.register(authRoutes, { prefix: '/api/v1/auth' })
  app.register(brandRoutes, { prefix: '/api/v1/brands' })
  app.register(dashboardRoutes, { prefix: '/api/v1/dashboard' })
  app.register(roadmapRoutes, { prefix: '/api/v1/roadmap' })
  app.get('/api/v1/profile', { preHandler: requireAuth }, async (request, reply) => { const profile = await prisma.profile.findUnique({ where: { userId: request.user!.id }, include: { user: { select: { id: true, phone: true, email: true, firstName: true, lastName: true, role: true } } } }); if (!profile) return reply.code(404).send({ ok: false, error: { code: 'PROFILE_NOT_FOUND', message: 'پروفایل پیدا نشد.' } }); return { ok: true, data: profile } })
  app.get('/api/v1/admin/stats', { preHandler: [requireAuth, requireRole('ADMIN', 'SUPER_ADMIN')] }, async () => { const [users, brands, analyses, payments] = await Promise.all([prisma.user.count(), prisma.brandProfile.count(), prisma.brandAnalysis.count(), prisma.payment.aggregate({ _sum: { amount: true }, where: { status: 'PAID' } })]); return { ok: true, data: { users, brands, analyses, paidAmount: payments._sum.amount ?? 0 } } })
  app.setErrorHandler((error, request, reply) => { if (error instanceof ZodError) return reply.code(400).send({ ok: false, error: { code: 'VALIDATION_ERROR', message: 'اطلاعات ورودی معتبر نیست.', details: error.flatten() } }); request.log.error(error); return reply.code((error as { statusCode?: number }).statusCode ?? 500).send({ ok: false, error: { code: 'INTERNAL_ERROR', message: 'خطای داخلی سرویس.' } }) })
  return app
}

const app = buildApp()
app.listen({ port: env.PORT, host: '0.0.0.0' }).catch(async (error) => { app.log.error(error); await closeDatabase(); process.exit(1) })
