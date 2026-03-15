# Redis connection troubleshooting

## Error: `getaddrinfo for host "y0o8gkwcow8gks80ooc8g8c4" port 6379: Temporary failure in name resolution`

This means the **Redis hostname is wrong or not set**. The app is trying to reach a host that doesn’t exist or isn’t resolvable in your environment.

### Fix

1. **Set the correct Redis URL** in your deployment (Coolify / Railway / Render / etc.):
   - If you have a **Redis service** in the same project (e.g. Coolify Redis):  
     `REDIS_URL=redis://redis:6379/0`  
     (Use the actual service name if it’s different; often it’s `redis`.)
   - If you use an **external Redis** (Upstash, Redis Cloud, etc.):  
     `REDIS_URL=redis://default:YOUR_PASSWORD@your-redis-host:6379/0`

2. **Remove or correct** any of these if they point to a wrong/placeholder host:
   - `REDIS_HOST` – should be the Redis hostname only (e.g. `redis`), **or** leave unset and use only `REDIS_URL`.
   - `REDIS_URL` – must use a **resolvable** host (not a placeholder like `y0o8gkwcow8gks80ooc8g8c4`).

3. **Optional**: If you don’t need background tasks (Celery), you can leave Redis unset. The web app and “View Details” will still work; only scheduled/async tasks will be disabled.

### Note

- **Sessions** use signed cookies, not Redis. The “Internal Server Error” on View Details is usually **not** caused by Redis.
- After changing env vars, **redeploy** so the new values are used.
