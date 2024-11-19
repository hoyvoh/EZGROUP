# Running the EZGROUP API Server with Docker Compose

This guide will help you set up and run the entire server stack (API, MySQL, Redis) using Docker Compose.

## Prerequisites

Before you begin, make sure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Setting Up the Project

1. Clone this repository:

   ```bash
   git clone https://github.com/hoyvoh/EZGROUP.git
   cd api
2. Ensure that your .env file is set up with the appropriate environment variables for your Django project. This includes sensitive information like database credentials. Example .env:
   ```bash
   MYSQL_ROOT_PASSWORD=root_password
   MYSQL_DATABASE=django_db
   MYSQL_USER=django_user
   MYSQL_PASSWORD=django_password

## Steps to Start the Server
1. Build and Start the Containers
Run the following command to build the Docker images and start the containers:
   ```bash
   docker-compose up --build
This will:
- Build the Docker images defined in the Dockerfile.
- Create the necessary containers for the Django API, MySQL database, and Redis server.
- Start the services in the correct order.

2. Initialize the Database
After the containers are up, the MySQL container will automatically create the database and user using the values from your .env file. However, in case you need to run database migrations or load initial data, follow the steps below:

Run Database Migrations:
- Open a terminal to access the running Django container:
   ```bash
   docker-compose exec api /bin/sh
- Run the migrations:
   ```bash
  python manage.py migrate
3. Verify the Setup
Once everything is running, you should be able to:
- Access the Django API by navigating to http://localhost:8000.
- Check MySQL and Redis connections through Django’s ORM and caching mechanisms, respectively.
4. Stop the Services
To stop the services and remove the containers, use:
  ```bash
  docker-compose down
This will stop the containers and remove them, but the data will persist in the volumes if you need to restart later.
 
