import type { FastifyInstance } from 'fastify'
import { z } from 'zod'
import { prisma } from '../../db/client.js'
import { requireAuth } from '../../middleware/auth.js'

const brandSchema = z.object({ name: z.string().min(2).max(120), industry: z.string().max(120).optional(), audience: z.string().max(500).optional(), tone: z.string().max(120).optional() })

export async function brandRoutes(app: FastifyInstance) {
  app.addHook('preHandler', requireAuth)
  app.get('/', async (request) => ({ ok: true, data: await prisma.brandProfile.findMany({ where: { userId: request.user!.id }, orderBy: { createdAt: 'asc' } }) }))
  app.post('/', async (request, reply) => { const input = brandSchema.parse(request.body); const brand = await prisma.brandProfile.create({ data: { ...input, userId: request.user!.id } }); return reply.code(201).send({ ok: true, data: brand }) })
  app.patch('/:brandId', async (request, reply) => { const input = brandSchema.partial().parse(request.body); const params = z.object({ brandId: z.string().cuid() }).parse(request.params); const result = await prisma.brandProfile.updateMany({ where: { id: params.brandId, userId: request.user!.id }, data: input }); if (!result.count) return reply.code(404).send({ ok: false, error: { code: 'BRAND_NOT_FOUND', message: 'برند پیدا نشد.' } }); return { ok: true, data: await prisma.brandProfile.findUnique({ where: { id: params.brandId } }) } })
}
