# MQWorkerService

This component of our project is responsible for grabbing data from [MET](https://frost.met.no/howto.html)
, processing it using the [DYNAMIC Fire risk indicator implementation library](https://pypi.org/project/dynamic-frcm/)
, and then writing it to a PostgreSQL database and publishing some of the data to RabbitMQ

## How to run locally

**This project assumes that the database and RabbitMQ are running on the same host/IP address.**

1. Clone the repository and create a `.env` file in the project root.

2. The `.env` file should contain the following variables (use `KEY=value` format, no spaces around `=`):

   - `IP` – The IP address where the database and RabbitMQ are running
   - `MET_CLIENT_ID` – Client ID from MET
   - `MET_CLIENT_SECRET` – Client secret from MET
   - `DB_NAME` – Name of the database
   - `DB_USER` – Database username
   - `DB_PASSWORD` – Database password

3. Make sure Docker is running.

4. From the root of the project (on Windows), run:
    `docker compose up --build app` from the root of the project (on Windows) and it should work.

## Caveats

This app requires a running PostgreSQL database and RabbitMQ instance.

We used the following official Docker images:

- [RabbitMQ](https://hub.docker.com/_/rabbitmq)  
- [PostgreSQL](https://hub.docker.com/_/postgres)

Strictly speaking, we actually used [PostGIS](https://hub.docker.com/r/postgis/postgis/) 
because we were potentially planning to use the PostGIS extension in our database. 
However, using PostGIS is not required for the app to function.