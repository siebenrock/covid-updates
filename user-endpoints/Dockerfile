FROM python:3
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["flask"]

# You can change this to a newer version of MySQL available at
# https://hub.docker.com/r/mysql/mysql-server/tags/
# FROM mysql/mysql-server:8.0.19

# Add timezone data
# RUN yum install -y tzdata && \
    # yum clean all && \
    # rm -rf /var/cache/yum

# COPY config/user.cnf /etc/mysql/my.cnf

CMD ["run", "--host=0.0.0.0"]
