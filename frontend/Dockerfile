FROM node:22

WORKDIR /frontend

COPY root/package.json root/package-lock.json ./root

WORKDIR /frontend/root

RUN ["npm", "ci"]

COPY root/ .

CMD ["npm", "run", "dev"]