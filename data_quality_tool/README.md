# Data Quality Tool and Frontend Setup

This project consists of a backend service (`data_quality_tool`) and a frontend service (`frontend`). The backend provides an API for Excel and JSON conversion and validation, while the frontend provides a user interface to interact with these features.

## Prerequisites

- Docker
- Docker Compose

## Installation Instructions

### Step 1: Install Docker and Docker Compose

#### Windows and macOS
- Download and install Docker Desktop from [Docker's official website](https://www.docker.com/products/docker-desktop).

#### Linux
- Follow the instructions on the [Docker website](https://docs.docker.com/engine/install/) to install Docker.
- Install Docker Compose by following the instructions [here](https://docs.docker.com/compose/install/).

### Step 2: Clone the Repository

Clone this repository to your local machine:

```sh
git clone https://github.com/madgik/datacatalog.git
cd datacatalog/data-quality-tool
```

### Step 3: Build and Run the Services

1. Build the services:

    ```sh
    docker-compose build
    ```

2. Start the services:

    ```sh
    docker-compose up -d
    ```

### Step 4: Access the Application

- The backend service will be available at [http://localhost:8000](http://localhost:8000).
- The frontend service will be available at [http://localhost:8080](http://localhost:8080).

You can now interact with the frontend to use the backend's functionality.

### Stopping the Services

To stop the services, run:

```sh
docker-compose down
```

## Additional Information

- To rebuild the images after making changes to the code, run `docker-compose build` again.
- To view logs for debugging, use `docker-compose logs -f`.
