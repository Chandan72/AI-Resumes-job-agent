FROM node:20-alpine

WORKDIR /app

COPY frontend/package.json /app/package.json
COPY frontend/vite.config.js /app/vite.config.js
COPY frontend/index.html /app/index.html
COPY frontend/src /app/src

RUN npm install --no-audit --no-fund

EXPOSE 5173

ENV VITE_API_BASE_URL=http://localhost:8000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]