FROM node:22-alpine AS build
WORKDIR /app

COPY nesharo-ui/backend/package*.json ./
RUN npm install

COPY nesharo-ui/backend/prisma ./prisma
RUN npx prisma generate
COPY nesharo-ui/backend/tsconfig.json ./
COPY nesharo-ui/backend/src ./src
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production

COPY --from=build /app/package*.json ./
RUN npm install --omit=dev
COPY --from=build /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=build /app/node_modules/@prisma ./node_modules/@prisma
COPY --from=build /app/dist ./dist

EXPOSE 10000
CMD ["node", "dist/server.js"]
