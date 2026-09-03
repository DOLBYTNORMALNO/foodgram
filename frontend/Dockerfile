# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json yarn.lock ./
# yarn.lock фиксирует версии из истории проекта (например, react-tooltip 5.21.6);
# npm install ставит свежие пакеты, несовместимые с этим кодом
RUN yarn install --frozen-lockfile
COPY . ./
RUN yarn build
CMD cp -r build result_build
