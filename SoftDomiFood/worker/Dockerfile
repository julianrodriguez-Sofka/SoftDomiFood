FROM node:20-slim

WORKDIR /app

# Instalar OpenSSL
RUN apt-get update -y && apt-get install -y openssl

# Copiar archivos de dependencias
COPY package*.json ./
COPY prisma ./prisma/

# Instalar dependencias
RUN npm install

# Generar Prisma Client
RUN npx prisma generate

# Copiar código fuente
COPY . .

# Comando por defecto
CMD ["npm", "run", "dev"]

