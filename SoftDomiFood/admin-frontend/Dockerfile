FROM node:20-slim

WORKDIR /app

# Copiar archivos de dependencias primero (para mejor caché)
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Exponer puerto
EXPOSE 3001

# Comando por defecto
CMD ["npm", "run", "dev"]

