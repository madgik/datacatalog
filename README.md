# DataCatalog

## Overview

DataCatalog (DC) is a component of the [Medical Informatics Platform](https://mip.ebrains.eu/) (MIP) under the [EBRAINS](https://www.ebrains.eu/) initiative. It enables seamless management, visualization, and access to data models and medical conditions.

### Key Features

- **Data Presentation:** Displays medical conditions linked to datasets within the MIP.
- **Visualization:** Interactive tools for exploring Common Data Elements (CDEs) and metadata hierarchies.
- **Data Management:** Create, edit, delete, and version control data models using XLSX and JSON file formats.
- **Role-Based Access:** Secure access and operation control via defined user roles and Keycloak integration.

## User Roles and Permissions

### Defined Roles

- **DOMAIN\_EXPERT**:
  - Responsible for creating, editing, deleting, and releasing unreleased data models.
- **DC\_ADMIN**:
  - Manages federations and all associated functionalities.

### Permissions Summary

| Feature                | DOMAIN\_EXPERT | DC\_ADMIN |
|------------------------|----------------|------------|
| Create/Edit Data Model | Yes            | No         |
| Delete Data Model      | Yes            | No         |
| Manage Federations     | No             | Yes        |
| Release Data Models    | Yes            | No         |

**Note:** Once a data model is released, it becomes immutable and cannot be modified or deleted.

## Features

### Informative Features (No Login Required)

Users can access the following features without logging in:

#### Federations

- View all available federations.
- Access detailed federation information.
- Navigate to the public URL of each federation.

#### Data Models

- Browse all released data models within federations.
- View detailed metadata.
- Visualize metadata hierarchies using a zoomable tidy tree.
- Access CDE-specific information.
- Download data models in JSON or XLSX format.

### Management Features (Login Required)

Authenticated users with proper roles gain access to management features, including:

- **Manage Federations:** Full control over federations (DC\_ADMIN).
- **Manage Data Models:** Create, edit, delete, and release unreleased data models (DOMAIN\_EXPERT).

## Installation and Setup

### Prerequisites

- Docker
- Docker Compose

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/madgik/datacatalog.git
   cd datacatalog
   ```

2. Create a `.env` file in the project root with the following configurations:

   ```env
   # Flask Environment
   FLASK_ENV=development
   FLASK_DEBUG=1

   # Database
   POSTGRES_PASSWORD=test
   
   # Backend Configuration
   DB_URL=jdbc:postgresql://datacatalogdb:5432/postgres
   DB_USER=postgres
   DB_PASSWORD=test
   PUBLIC_HOST=http://localhost ; In case of having frontend on development set this to 'http://localhost:4200'.
   DQT_URL=http://data_quality_tool:8000

   # Keycloak Authentication
   AUTHENTICATION=1
   KEYCLOAK_AUTH_URL=https://iam.ebrains.eu/auth/
   KEYCLOAK_REALM=MIP
   KEYCLOAK_CLIENT_ID=datacatalogue
   KEYCLOAK_CLIENT_SECRET=your_secret_here
   KEYCLOAK_SSL_REQUIRED=none
   ```

3. Deploy using Docker Compose:

   ```bash
   docker-compose up --build
   ```

4. Access the application in your browser at [http://localhost](http://localhost).

## Development Setup

For development purposes, you can run the frontend and backend separately:

### Frontend

1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```

2. Install dependencies using npm:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   ng serve
   ```

---

**DataCatalog** is maintained by the Medical Informatics Platform team under EBRAINS. For more information, visit [EBRAINS](https://www.ebrains.eu/).

