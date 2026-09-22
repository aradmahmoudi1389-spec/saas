import { writeFileSync } from 'node:fs'

const document = {
  openapi: '3.0.3',
  info: { title: 'Nesharo API', version: '1.0.0', description: 'Personal Brand Intelligence API' },
  servers: [{ url: 'http://localhost:4000' }],
  paths: {
    '/api/v1/auth/register': { post: { summary: 'Create a user account' } },
    '/api/v1/auth/login': { post: { summary: 'Create a secure session' } },
    '/api/v1/auth/logout': { post: { summary: 'Revoke current session' } },
    '/api/v1/profile': { get: { summary: 'Get current user profile', security: [{ cookieAuth: [] }] } },
    '/api/v1/brands': { get: { summary: 'List brands' }, post: { summary: 'Create brand' } },
    '/api/v1/dashboard': { get: { summary: 'Get dashboard aggregate' } },
    '/api/v1/roadmap': { get: { summary: 'List roadmaps and tasks' } },
    '/api/v1/roadmap/tasks/{taskId}': { patch: { summary: 'Update task progress' } },
    '/api/v1/admin/stats': { get: { summary: 'Get admin statistics' } },
  },
  components: { securitySchemes: { cookieAuth: { type: 'apiKey', in: 'cookie', name: 'session' } } },
}

if (process.argv[1]?.endsWith('openapi.ts')) writeFileSync('openapi.json', JSON.stringify(document, null, 2))
export default document
