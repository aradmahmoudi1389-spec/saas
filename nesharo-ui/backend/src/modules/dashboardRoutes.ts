import type { FastifyInstance } from 'fastify'
import { z } from 'zod'
import { prisma } from '../db/client.js'
import { requireAuth } from '../middleware/auth.js'

export async function dashboardRoutes(app: FastifyInstance) {
  app.get('/', { preHandler: requireAuth }, async (request, reply) => {
    const userId = request.user!.id
    const [brands, analysis, roadmap, content, notifications] = await Promise.all([
      prisma.brandProfile.findMany({ where: { userId } }),
      prisma.brandAnalysis.findFirst({ where: { userId }, orderBy: { createdAt: 'desc' }, include: { scores: true } }),
      prisma.roadmap.findFirst({ where: { userId }, orderBy: { createdAt: 'desc' }, include: { tasks: true } }),
      prisma.content.findMany({ where: { userId }, orderBy: { createdAt: 'desc' }, take: 5 }),
      prisma.notification.findMany({ where: { userId, readAt: null }, orderBy: { createdAt: 'desc' }, take: 5 }),
    ])
    return { ok: true, data: { brands, analysis, roadmap, recentContent: content, unreadNotifications: notifications } }
  })
}

export async function roadmapRoutes(app: FastifyInstance) {
  app.addHook('preHandler', requireAuth)
  app.get('/', async (request) => ({ ok: true, data: await prisma.roadmap.findMany({ where: { userId: request.user!.id }, include: { tasks: true }, orderBy: { createdAt: 'desc' } }) }))
  app.patch('/tasks/:taskId', async (request, reply) => { const params = z.object({ taskId: z.string().cuid() }).parse(request.params); const body = z.object({ status: z.enum(['TODO','IN_PROGRESS','DONE']).optional(), progress: z.number().int().min(0).max(100).optional() }).parse(request.body); const task = await prisma.roadmapTask.findFirst({ where: { id: params.taskId, roadmap: { userId: request.user!.id } } }); if (!task) return reply.code(404).send({ ok: false, error: { code: 'TASK_NOT_FOUND', message: 'وظیفه پیدا نشد.' } }); return { ok: true, data: await prisma.roadmapTask.update({ where: { id: task.id }, data: body }) } })
}
