FROM node:18-bullseye-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true
ENV PORT=3000

EXPOSE 3000

CMD ["npm", "run", "dev"]
