# FLASK APPLICATION

### This project is a simple flask application that works as frontend for the MongoDB cluster. This app allows the user to visualize the data stored in the database, perform son basic CRUD operations and run some queries.

## Rquirements

- Docker
- Docker-compose

## Project Structure

mi_proyecto_flask/
│
├── app
|    └──                  # Main application file
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration to build the image
├── docker-compose.yml    # Docker Compose configuration to run the container
├── templates/            # HTML templates
│   └── index.html
└── static/               # Static files
    ├── scripts.js
    └── styles.css

## How to run the project

1. **Build and run the container**:

    ```bash
    docker-compose up --build
    ```
    ***Note: if you already have the image built, you can run the container without the --build flag.***

2. **Access the application**:

    Open your browser and go to http://localhost:5000

3. **Stop the container**:
    ```bash
    docker-compose down
    ```
    ***Note: if you want to remove the volumes add the "-v" flag.***

