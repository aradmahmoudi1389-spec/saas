FROM node:22-alpine AS build
WORKDIR /app

COPY nesharo-ui/backend/package*.json ./
RUN npm install

ENV DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres" \
    DIRECT_URL="postgresql://postgres:postgres@localhost:5432/postgres"
COPY nesharo-ui/backend/prisma ./prisma
RUN npx prisma generate
COPY nesharo-ui/backend/tsconfig.json ./
COPY nesharo-ui/backend/src ./src
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production

COPY --from=build /app/package*.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/prisma ./prisma
COPY --from=build /app/dist ./dist

EXPOSE 10000
CMD ["sh", "-c", "npx prisma db push --accept-data-loss && node dist/server.js"]
