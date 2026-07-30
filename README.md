# 🚀 videofix_backend

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/NicolausFeldtmann/videofix_backend?style=for-the-badge)](https://github.com/NicolausFeldtmann/videofix_backend/stargazers)

[![GitHub forks](https://img.shields.io/github/forks/NicolausFeldtmann/videofix_backend?style=for-the-badge)](https://github.com/NicolausFeldtmann/videofix_backend/network)

[![GitHub issues](https://img.shields.io/github/issues/NicolausFeldtmann/videofix_backend?style=for-the-badge)](https://github.com/NicolausFeldtmann/videofix_backend/issues)

[![GitHub license](https://img.shields.io/github/license/NicolausFeldtmann/videofix_backend?style=for-the-the-badge)](LICENSE) <!-- TODO: Add a LICENSE file -->

**A robust Django REST API backend for video management and user authentication.**

[Live Demo](https://demo-link.com) <!-- TODO: Add live demo link if available -->

</div>

## 📖 Overview

The `videofix_backend` is a powerful and scalable API service built with Django and Django REST Framework. It serves as the core backend for a video-centric application, providing essential functionalities for user authentication and comprehensive video content management. The project is designed with modularity, utilizing separate Django apps for `auth_app` and `video_app` to ensure clear separation of concerns and maintainability.

Leveraging Docker and Docker Compose, this backend offers an easy-to-set-up development environment and streamlined deployment. It includes features like JWT-based authentication, PostgreSQL database integration, and automatically generated API documentation using DRF Spectacular.

## ✨ Features

-   **🔐 Robust User Authentication**: Secure user registration, login, and JWT-based token management using `auth_app`.
-   **🎞️ Comprehensive Video Management**: Functionality to upload, store, and retrieve video content via the `video_app`.
-   **⚙️ RESTful API**: A well-structured and performant API built with Django REST Framework, ensuring easy integration with frontend applications.
-   **📄 Automatic API Documentation**: Integrated Swagger UI / ReDoc for interactive API exploration and documentation, powered by `drf-spectacular`.
-   **🐳 Dockerized Environment**: Full Docker and Docker Compose support for simplified setup, development, and deployment.
-   **💾 PostgreSQL Database**: Reliable and scalable data storage with PostgreSQL.
-   **☁️ Cloud Storage Integration**: Ready for cloud file storage solutions with `django-storages` (e.g., AWS S3).

## 🛠️ Tech Stack

**Backend:**

![Python](https://img.shields.io/badge/Python-3.9-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)

![Django](https://img.shields.io/badge/Django-4.2-092E20.svg?style=for-the-badge&logo=django&logoColor=white)

![Django REST Framework](https://img.shields.io/badge/DRF-3.14-092E20.svg?style=for-the-badge&logo=django&logoColor=white)

![Gunicorn](https://img.shields.io/badge/Gunicorn-Web_Server-499848.svg?style=for-the-badge&logo=gunicorn&logoColor=white)

![PyJWT](https://img.shields.io/badge/PyJWT-2.8-FF3333.svg?style=for-the-badge&logo=json-web-tokens&logoColor=white)

![Pillow](https://img.shields.io/badge/Pillow-10.x-5D4D47.svg?style=for-the-badge&logo=pillow&logoColor=white)

![DRF Spectacular](https://img.shields.io/badge/DRF%20Spectacular-0.27-563D7C.svg?style=for-the-badge)

**Database:**

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

**DevOps & Tools:**

![Docker](https://img.shields.io/badge/Docker-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)

![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)

![Bash](https://img.shields.io/badge/Shell_Script-121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)

## 🚀 Quick Start

This project uses Docker Compose for an easy and consistent development environment setup.

### Prerequisites

Before you begin, ensure you have the following installed:

-   **Docker Desktop**: Includes Docker Engine and Docker Compose.
    -   [Download for Windows/Mac](https://www.docker.com/products/docker-desktop/)
    -   [Install for Linux](https://docs.docker.com/engine/install/)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/NicolausFeldtmann/videofix_backend.git
    cd videofix_backend
    ```

2.  **Environment setup**
    Create a `.env` file in the project root by copying the example. You will need to configure your database credentials, Django secret key, and other settings.

    ```bash
    cp .env.example .env
    ```
    Edit `.env` and set the following variables:
    ```ini
    # Django settings
    SECRET_KEY=your_django_secret_key_here # IMPORTANT: Change this in production!
    DEBUG=True
    ALLOWED_HOSTS='*' # For development, specify actual hosts in production (e.g., 'localhost,127.0.0.1')

    # PostgreSQL settings (as defined in docker-compose.yml)
    POSTGRES_DB=videofix_db
    POSTGRES_USER=videofix_user
    POSTGRES_PASSWORD=videofix_password
    POSTGRES_HOST=db # 'db' is the service name in docker-compose.yml
    POSTGRES_PORT=5432

    # Optional: Superuser creation on first run if DEBUG=True
    # DJANGO_SUPERUSER_USERNAME=admin
    # DJANGO_SUPERUSER_EMAIL=admin@example.com

    # Optional: AWS S3 settings for django-storages (uncomment and configure if used)
    # AWS_ACCESS_KEY_ID=your_aws_access_key_id
    # AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
    # AWS_STORAGE_BUCKET_NAME=your_s3_bucket_name
    # AWS_S3_REGION_NAME=your_aws_region
    ```
    **Note**: It is highly recommended to generate a strong, unique `SECRET_KEY` for production environments.

3.  **Start the services**
    This command will build the Docker images, create the containers, and start the backend and PostgreSQL services. The `backend.entrypoint.sh` script will automatically run migrations.

    ```bash
    docker-compose up -d --build
    ```
    `-d` runs the containers in detached mode (in the background). `--build` ensures your images are freshly built.

4.  **Create a superuser (for Django Admin)**
    You'll need a superuser account to access the Django administrative interface.

    ```bash
    docker-compose exec backend python manage.py createsuperuser
    ```
    Follow the prompts to create your superuser account.

5.  **Access the API**
    The API will be available at `http://localhost:8000/`.

    You can access the interactive API documentation (Swagger UI) at:
    `http://localhost:8000/api/schema/swagger-ui/`

    And ReDoc documentation at:
    `http://localhost:8000/api/schema/redoc/`

## 📁 Project Structure

```
videofix_backend/
├── auth_app/                  # Django app for user authentication, registration, JWT handling
│   ├── migrations/            # Database migration files for auth models
│   ├── models.py              # User and authentication related database models
│   ├── serializers.py         # DRF serializers for auth models
│   ├── urls.py                # URL routing for authentication endpoints
│   └── views.py               # API view logic for authentication
├── backend.Dockerfile         # Dockerfile for building the backend service image
├── backend.entrypoint.sh      # Entrypoint script for the Docker container (waits for DB, runs migrations, starts Gunicorn)
├── core/                      # Main Django project configuration
│   ├── __init__.py
│   ├── settings.py            # Global Django settings and configurations
│   ├── urls.py                # Main URL dispatcher for the project
│   ├── asgi.py                # ASGI configuration (for async applications)
│   └── wsgi.py                # WSGI configuration (for synchronous applications)
├── docker-compose.yml         # Defines Docker services (backend, db) for multi-container applications
├── manage.py                  # Django's command-line utility for administrative tasks
├── requirements.txt           # Python dependencies for the project
├── video_app/                 # Django app for video related functionalities
│   ├── migrations/            # Database migration files for video models
│   ├── models.py              # Video related database models
│   ├── serializers.py         # DRF serializers for video models
│   ├── urls.py                # URL routing for video endpoints
│   └── views.py               # API view logic for video management
├── .dockerignore              # Specifies files/directories to ignore when building Docker images
├── .gitignore                 # Specifies files/directories to ignore from Git version control
└── .env.example               # Example environment variables file
```

## ⚙️ Configuration

### Environment Variables

The project uses environment variables for sensitive data and deployment-specific settings. A `.env.example` file is provided, which you should copy to `.env` and configure.

| Variable                  | Description                                            | Default (in `.env.example`) | Required |

| :------------------------ | :----------------------------------------------------- | :-------------------------- | :------- |

| `SECRET_KEY`              | Django secret key for cryptographic signing.           | `your_django_secret_key_here` | Yes      |

| `DEBUG`                   | Set to `True` for development, `False` for production. | `True`                      | Yes      |

| `ALLOWED_HOSTS`           | Comma-separated list of allowed hostnames for the app. | `'*'`                       | Yes      |

| `POSTGRES_DB`             | PostgreSQL database name.                              | `videofix_db`               | Yes      |

| `POSTGRES_USER`           | PostgreSQL database user.                              | `videofix_user`             | Yes      |

| `POSTGRES_PASSWORD`       | PostgreSQL database password.                          | `videofix_password`         | Yes      |

| `POSTGRES_HOST`           | PostgreSQL database host.                              | `db`                        | Yes      |

| `POSTGRES_PORT`           | PostgreSQL database port.                              | `5432`                      | Yes      |

| `DJANGO_SUPERUSER_USERNAME` | Username for optional superuser creation on startup.   | (Not set)                   | No       |

| `DJANGO_SUPERUSER_EMAIL`  | Email for optional superuser creation on startup.      | (Not set)                   | No       |

| `AWS_ACCESS_KEY_ID`       | AWS access key for S3 storage.                         | (Not set)                   | No       |

| `AWS_SECRET_ACCESS_KEY`   | AWS secret key for S3 storage.                         | (Not set)                   | No       |

| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name for file storage.                       | (Not set)                   | No       |

| `AWS_S3_REGION_NAME`      | AWS region for S3 bucket.                              | (Not set)                   | No       |

### Configuration Files

-   `core/settings.py`: The main Django settings file, where you can find general project configurations, installed apps, middleware, template settings, and more. Environment variables defined in `.env` are loaded and used here.

## 🔧 Development

### Local Setup (without Docker Compose)

If you prefer to run the backend locally without Docker Compose, ensure you have Python 3.9+ and PostgreSQL installed.

1.  **Install Python dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Database setup**
    Ensure your PostgreSQL database is running and configured according to your `.env` file.
    Then, apply database migrations:
    ```bash
    python manage.py makemigrations auth_app video_app core
    python manage.py migrate
    ```

3.  **Create a superuser**
    ```bash
    python manage.py createsuperuser
    ```

4.  **Start development server**
    ```bash
    python manage.py runserver
    ```
    The server will typically run on `http://localhost:8000/`.

### Available `manage.py` Commands

| Command                     | Description                                            |

| :-------------------------- | :----------------------------------------------------- |

| `python manage.py runserver`  | Starts the development server.                         |

| `python manage.py makemigrations [app_name]` | Creates new database migrations based on model changes. |

| `python manage.py migrate`    | Applies database migrations.                           |

| `python manage.py createsuperuser` | Creates an administrative user.                        |

| `python manage.py collectstatic` | Collects static files into STATIC_ROOT.                |

| `python manage.py test`       | Runs tests for the project.                            |

| `python manage.py shell`      | Opens a Python shell with Django environment loaded.   |

## 🧪 Testing

This project uses Django's built-in testing framework.

```bash

# Run all tests
docker-compose exec backend python manage.py test

# Run tests for a specific app (e.g., auth_app)
docker-compose exec backend python manage.py test auth_app
```

## 🚀 Deployment

The project is designed for containerized deployment using Docker.

### Production Build

The `backend.Dockerfile` is optimized for production. To build the production image:

```bash
docker build -f backend.Dockerfile -t videofix_backend:latest .
```

### Deployment Options

-   **Docker Compose**: The `docker-compose.yml` can be adapted for production environments, potentially adding services like Nginx, Certbot, etc. Ensure environment variables are properly set for production.
-   **Kubernetes**: The Docker image can be deployed to Kubernetes clusters using appropriate deployment and service configurations.
-   **Cloud Platforms**: Deploy directly to platforms like AWS ECS, Google Cloud Run, Azure Container Instances, or other services that support Docker containers.

## 📚 API Reference

This project utilizes `drf-spectacular` to automatically generate OpenAPI 3.0 schema and interactive API documentation.

-   **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
-   **ReDoc**: `http://localhost:8000/api/schema/redoc/`

### Authentication

The API uses JWT (JSON Web Tokens) for authentication.

1.  **Obtain Token**: Send a `POST` request to `/api/auth/token/` with `username` and `password`.
    ```json
    {
        "email": "user@example.com",
        "password": "yourpassword"
    }
    ```
    This will return an `access` and `refresh` token.

2.  **Authenticate Requests**: Include the `access` token in the `Authorization` header for protected endpoints:
    `Authorization: Bearer <your_access_token>`

3.  **Refresh Token**: If the access token expires, use the `refresh` token to get a new access token: `POST` to `/api/auth/token/refresh/`.

### Example Endpoints

The following are examples of potential API endpoints. Refer to the Swagger UI/ReDoc for the full, up-to-date list and details.

#### Authentication

-   `POST /api/auth/register/` - Register a new user.
-   `POST /api/auth/token/` - Obtain JWT access and refresh tokens.
-   `POST /api/auth/token/refresh/` - Refresh an expired access token.
-   `GET /api/auth/me/` - Get details of the authenticated user. (Requires authentication)

#### Video Management

-   `GET /api/videos/` - List all videos. (May require authentication)
-   `POST /api/videos/` - Upload a new video. (Requires authentication)
-   `GET /api/videos/{id}/` - Retrieve details of a specific video.
-   `PUT /api/videos/{id}/` - Update a specific video. (Requires authentication)
-   `DELETE /api/videos/{id}/` - Delete a specific video. (Requires authentication)

## 🤝 Contributing

We welcome contributions! If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

### Development Setup for Contributors

Follow the **Quick Start** instructions to get the development environment running.
Ensure your code adheres to PEP 8 guidelines.

## 📄 License

This project is licensed under the [LICENSE_NAME](LICENSE) - see the LICENSE file for details. <!-- TODO: Add a LICENSE file, e.g., MIT, Apache 2.0 -->

## 🙏 Acknowledgments

-   **Django**: The web framework that powers this project.
-   **Django REST Framework**: For building powerful and flexible APIs.
-   **PostgreSQL**: The robust and open-source relational database.
-   **Docker**: For containerizing the application and its dependencies.
-   **NicolausFeldtmann**: The original author and maintainer of this repository.

## 📞 Support & Contact

-   🐛 Issues: [GitHub Issues](https://github.com/NicolausFeldtmann/videofix_backend/issues)
-   👤 Owner: [NicolausFeldtmann](https://github.com/NicolausFeldtmann)

---

<div align="center">

Made by NicolausFeldtmann

</div>

