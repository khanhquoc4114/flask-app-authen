FROM node:18-bullseye-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=development
ENV PORT=3000

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]
