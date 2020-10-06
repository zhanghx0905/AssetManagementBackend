# First stage, build the frontend
# TO DO

# FROM node:12.18.3

# RUN npm config set registry https://registry.npm.taobao.org

# ENV FRONTEND=/opt/frontend

# WORKDIR $FRONTEND

# COPY frontend/package.json $FRONTEND
# COPY frontend/package-lock.json $FRONTEND
# RUN npm install

# COPY frontend/ $FRONTEND
# RUN npm run build

# Second stage for the backend
FROM python:3.7.9

ENV HOME=/opt/app

WORKDIR $HOME

COPY requirements.txt $HOME
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . $HOME

# # Copy frontend from the first stage
# COPY --from=0 /opt/frontend/build frontend/build

EXPOSE 80

ENV PYTHONUNBUFFERED=true
CMD ["/bin/sh", "config/run.sh"]
