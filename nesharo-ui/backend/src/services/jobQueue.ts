export type JobName = 'brand-analysis' | 'content-analysis' | 'instagram-sync' | 'report-generation' | 'notification'
export type JobPayload = Record<string, unknown>

export type Job = { id: string; name: JobName; payload: JobPayload; createdAt: Date }

export interface JobQueue {
  enqueue(name: JobName, payload: JobPayload): Promise<Job>
}

export class InMemoryJobQueue implements JobQueue {
  private jobs: Job[] = []
  async enqueue(name: JobName, payload: JobPayload): Promise<Job> {
    const job = { id: crypto.randomUUID(), name, payload, createdAt: new Date() }
    this.jobs.push(job)
    return job
  }
  list() { return [...this.jobs] }
}
