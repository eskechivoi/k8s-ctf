# --- STAGE 1: BUILDER (Install dependencies and compile) ---
FROM node:20-slim AS builder

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm ci

COPY . .

RUN npm run build

# --- STAGE 2: RUNNER (Production Runtime) ---
FROM node:20-slim AS runner

WORKDIR /app

ENV PORT=3000

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

CMD ["npm", "start"]