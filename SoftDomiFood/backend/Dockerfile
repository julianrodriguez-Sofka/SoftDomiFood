FROM node:20-slim

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./
COPY prisma ./prisma/

# Instalar dependencias
RUN npm install

# Generar Prisma Client
RUN npx prisma generate

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 5000

# Comando por defecto (puede ser sobrescrito en docker-compose)
CMD ["npm", "run", "dev"]


