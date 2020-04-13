# create a new network for my webserver container and my sql database container
docker network create user-network

# create the docker image for the server and create the server container
docker build -t userserver .

docker run  -dit --name=user-server-container --network user-network -e FLASK_APP=UserBackend.py -p 5000:5000 userserver

# run mysql container but add it to my-network
docker run --name user-db-container -e MYSQL_ROOT_PASSWORD=pass -e MYSQL_DATABASE=users -v //c//Users//ari11//Documents//github//backend-project//user-endpoints//db://db --network user-network -dit mysql:latest --default-authentication-plugin=mysql_native_password

# useful mysql commands

# Let's now tell docker to execute a command (bash) in the database-container container and make it interactive so that we can run commands inside the database-container container in another process (i.e. don't stop the mysql process within the docker container)
docker exec -it user-db-container bash

# Now we are inside the mysql container in a separate process. Let's run the mysql client app so that we can execute SQL queries
mysql -uroot -p

# Let's now display all of the databases inside the MySQL instance
show databases;

# Let's select the demo database we created on initialization
use tasks;

# We are now in the database. We can now create tables and run query commands. To verify that we have no tables, let's view all of the tables;
show tables;

# create table
CREATE TABLE users (
    id int unsigned not null auto_increment primary key,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    zipcode VARCHAR(30) NOT NULL
);

# add attribute to table
ALTER TABLE tasks ADD notify VARCHAR(50) NOT NULL