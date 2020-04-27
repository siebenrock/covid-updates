# COVID-19 API

Given a user’s location, our service will return the updated number of COVID-19 cases in their county.  A user can enter their name, phone number, and zipcode to sign up. Once subscribed, they will receive a daily text message with updated statistics.

# Why We Built It

Given the current situation with COVID-19, we decided to explore the possibility of implementing an API that will deliver useful information to any person interested in knowing more about the virus.
For this reason, we worked on an API that will get the most recent COVID-19 confirmed/recovered/deaths cases and delivered this information based on user location.

## Diagram



## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

For you to run this API the following dependencies should be installed:

* flask
* flask_restful
* mysqlclient
* requests
* uszipcode
* twilio
* apscheduler

Apart from this python libraries is important to have docker installed.

Note: for Windows users please install docker toolbox.

### Installing

To start a local working version of this project, follow the next steps:

In your CMD run

```
docker network create <name-of-network>
```

inside the user-endpoints directory run. The command bellow assumes the existence of Dockerfile.

```
docker build -t <image name> .
```

To start the docker container "image name" run:

```
docker run  -dit --name=<container name> --network <name-of-network> -e FLASK_APP=UserBackend.py -p 5000:5000 <image-name>
```
Then install the following MySQL image:

```
docker run --name <name-of-db-container> -e MYSQL_ROOT_PASSWORD=<password> -e MYSQL_DATABASE=<name of database> -v path/to/db://db --network <name-of-network> -dit mysql:latest --default-authentication-plugin=mysql_native_password
```
The above command will:

1. Download MySQL image
2. Create a new database with credentials passwod.
3. Start the container with name: name-of-db-container

For more useful commands please check the setup.sh inside user-endpoints directory.

## Running the tests

To run tests for the userserver endpoints (this endpoints register new user and send messages via Twilio) run:

```
# run this inside user-endpoints directory
python tests.py
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web development used
* [twilio](https://maven.apache.org/) - Dependency Management
* [Docker](https://www.docker.com/) - Container
* [MySQL](https://www.mysql.com/) - Database used
* [CSSEGISandData](https://github.com/CSSEGISandData/COVID-19) - Where we get the data
  
## Authors

See also the list of [contributors](https://github.com/siebenrock/backend-project/graphs/contributors) who participated in this project.


