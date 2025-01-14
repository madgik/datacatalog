# DataCatalogue

## Overview

DataCatalogue (DC) is a component of the [Medical Informatics Platform](https://mip.ebrains.eu/) (MIP) for [EBRAINS](https://www.ebrains.eu/). It provides functionalities to:

- Present the medical conditions linked to data within the MIP.
- Present and visualize Common Data Elements (CDEs) data models associated with these medical conditions.
- Manage (create, edit, delete) data models, complete with version control, accessible by authorized accounts. Supported file formats include XLSX and JSON.

## User Roles and Permissions

### Roles

- **DOMAIN\_EXPERT**: Responsible for creating, editing, deleting, and releasing unreleased data models.
- **DC\_ADMIN**: Manages federations and all associated functionalities.

## Features

### Informative Features (No Login Required)

Without logging in, users can access the following features:

#### Federations

- View all available federations.
- Access detailed information for each federation.
- Navigate to the public URL of a federation.

#### Data Models

- Browse all released data models within each federation.
- View metadata details.
- Interact with a zoomable tree structure to visualize metadata hierarchies.
- Access detailed information about each CDE.
- Download JSON/XLSX data models 's hierarchy in a json format.

### Management Features (Login and Role Required)

Authenticated users, authorized through a Keycloak instance configured for MIP, gain access to management features:

- **DC\_ADMIN**: Complete control over all federation operations.
- **DOMAIN\_EXPERT**: Full permissions to create, edit, delete, and release unreleased data models.

**Note:** Released data models are immutable and cannot be edited or deleted.

## Installation and Setup

### System Requirements

- Docker
- Docker Compose

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/madgik/datacatalog.git
   cd datacatalog
   ```

### Docker Setup

This project includes a `docker-compose.yml` file for deploying services in Docker containers.

#### Steps to Deploy with Docker Compose

1. Install Docker and Docker Compose if not already installed.

2. Create a `.env` file in the project root and populate it with the following variables:

   ```env
   # Data Quality Tool
   FLASK_ENV=development
   FLASK_DEBUG=1

   # Database
   POSTGRES_PASSWORD=test

   # Backend
   DB_URL=jdbc:postgresql://datacatalog_db:5432/postgres
   DB_USER=postgres
   DB_PASSWORD=test
   PUBLIC_HOST=http://localhost:4200; this is the ip in case you want to have the frontend in development mode and not dockerized
   DQT_URL=http://data_quality_tool:8000

   # Keycloak
   AUTHENTICATION=1
   KEYCLOAK_AUTH_URL=https://iam.ebrains.eu/auth/
   KEYCLOAK_REALM=MIP
   KEYCLOAK_CLIENT_ID=datacatalogue
   KEYCLOAK_CLIENT_SECRET=your_secret_here
   KEYCLOAK_SSL_REQUIRED=none
   ```

3. Start the services:

   ```bash
   docker-compose up --build
   ```

4. Access the application at [http://localhost](http://localhost).

