FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# On expose sur toutes les interfaces réseau (host) pour que Docker laisse passer le trafic
CMD ["npm", "run", "dev", "--", "--host"]
