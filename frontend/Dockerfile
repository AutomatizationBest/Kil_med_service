FROM node:alpine

COPY package.json package.json
RUN npm install
COPY . .

# FROM nginx:stable-alpine

# COPY --from=build /dist /usr/share/nginx/html
# COPY --from=build nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
# CMD [ "nginx", "-g", "daemon off;" ]
CMD [ "npm", "start"]
# Этап сборки
# FROM node:alpine as build

# WORKDIR /app

# COPY package.json package-lock.json ./
# RUN npm install

# COPY . .
# RUN npm run build

# Этап продакшена
# FROM node:alpine

# WORKDIR /app

# COPY --from=build /app/dist ./dist
# COPY --from=build /frontend/package.json ./package.json
# COPY --from=build /frontend/package-lock.json ./package-lock.json

# RUN npm install --production

# EXPOSE 3000

# CMD [ "npm", "start" ]
