FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci && \
    npm install -D tailwindcss@latest postcss@latest autoprefixer@latest @tailwindcss/forms@latest
COPY . .
ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true
CMD ["npm", "start"]
