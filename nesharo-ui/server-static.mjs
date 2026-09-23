import { createServer } from 'node:http'
import { createReadStream, statSync } from 'node:fs'
import { extname, join, normalize } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = fileURLToPath(new URL('./dist/', import.meta.url))
const apiOrigin = 'https://saas-bg0w.onrender.com'
const types = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.txt', 'text/plain; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
  ['.jpg', 'image/jpeg'],
  ['.jpeg', 'image/jpeg'],
  ['.ico', 'image/x-icon'],
])

function sendFile(response, path) {
  response.setHeader('content-type', types.get(extname(path)) ?? 'application/octet-stream')
  createReadStream(path).pipe(response)
}

createServer(async (request, response) => {
  if (!request.url) return response.end()
  if (request.url.startsWith('/api/')) {
    const target = new URL(request.url, apiOrigin)
    const headers = new Headers(request.headers)
    headers.set('host', target.host)
    const upstream = await fetch(target, { method: request.method, headers, body: ['GET', 'HEAD'].includes(request.method ?? 'GET') ? undefined : request, duplex: 'half' })
    response.writeHead(upstream.status, Object.fromEntries(upstream.headers.entries()))
    if (upstream.body) upstream.body.pipeTo(new WritableStream({ write(chunk) { response.write(chunk) }, close() { response.end() } }))
    else response.end()
    return
  }
  const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname)
  const safePath = normalize(pathname).replace(/^(\.\.[/\\])+/, '')
  let filePath = join(root, safePath)
  try {
    if (statSync(filePath).isDirectory()) filePath = join(filePath, 'index.html')
    statSync(filePath)
  } catch {
    filePath = join(root, 'index.html')
  }
  sendFile(response, filePath)
}).listen(80, '0.0.0.0')
