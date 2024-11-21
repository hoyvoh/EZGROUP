# Running the EZGROUP API Server with Docker Compose

This guide will help you set up and run the entire server stack (API, MySQL, Redis) using Docker Compose.

## Prerequisites

Before you begin, make sure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Setting Up the Project

### 1. Clone this repository:

```bash
git clone https://github.com/hoyvoh/EZGROUP.git
cd api
```

### 2. Ensure that your .env file is set up with the appropriate environment variables for your Django project. This includes sensitive information like database credentials. Example .env:

```bash
DJANGO_SECRET_KEY=''
MYSQL_CONNECTION_NAME=''
DBNAME=''
USER=''
PASS=''
HOST=''
PORT=''
EMAIL_HOST=''
EMAIL_PORT=
EMAIL_USE_TLS=
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
EMAIL_APP_PASSWORD=''
DEFAULT_FROM_EMAIL=''
MAIL_RECOVERY_CODE=''
SSO_URL =''
```

You can also contact

## Steps to Start the Server

### 1. Build and Start the Containers

Run the following command to build the Docker images and start the containers:

```bash
docker-compose up --build
This will:
```

- Build the Docker images defined in the Dockerfile.
- Create the necessary containers for the Django API, MySQL database, and Redis server.
- Start the services in the correct order.

### 2. Initialize the Database

After the containers are up, the MySQL container will automatically create the database and user using the values from your .env file. However, in case you need to run database migrations or load initial data, follow the steps below:

Run Database Migrations:

- Open a terminal to access the running Django container:
  ```bash
  docker-compose exec api python manage.py migrate
  ```

### 3. Verify the Setup

Once everything is running, you should be able to:

- Access the Django API by navigating to http://localhost:8000.
- Check MySQL and Redis connections through Django’s ORM and caching mechanisms, respectively.

### 4. Accessing the MySQL Database

To interact with the MySQL database container, you can run the following:

```bash
docker exec -it mysql_container mysql -u root -p
```

You'll be prompted for the root password. Enter the password defined in your .env file.

### 5. Redis and Celery

To run Celery with Redis as the broker for background tasks, you'll need to start the Celery worker.

In a new terminal, run:

```bash
docker-compose exec api celery -A api worker --loglevel=info
```

You can now add tasks to the queue that Celery will process in the background.

### 6. Stop the Services

To stop the services and remove the containers, use:

```bash
docker-compose down
```

This will stop the containers and remove them, but the data will persist in the volumes if you need to restart later.
