FROM node:22-alpine AS base

WORKDIR /app


# Stage 1: Install dependencies
FROM base AS deps

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci


# Stage 2: Build the Next.js application
FROM base AS builder

ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

COPY --from=deps /app/node_modules ./node_modules

COPY frontend/ ./

RUN npm run build


# Stage 3: Production runtime
FROM base AS runner

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/public ./public

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./

COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
