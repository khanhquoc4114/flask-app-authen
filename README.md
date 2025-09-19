# Flask‑App‑Authen

> A sample Flask application that provides authentication via Google and GitHub OAuth.

---

## Table of Contents

- [Flask‑App‑Authen](#flaskappauthen)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Project Structure](#project-structure)
  - [Installation \& Running](#installation--running)
  - [Docker \& Docker Compose](#docker--docker-compose)
  - [🚀 Deployment](#-deployment)
    - [CI/CD Workflow](#cicd-workflow)
    - [Required Secrets](#required-secrets)
  - [Best Practices \& Future Improvements](#best-practices--future-improvements)

---

## Introduction

Flask‑App‑Authen is a sample project built with Flask (Python) designed to:

- Support user login via **Google** and **GitHub** OAuth.  
- Include both frontend & backend.  
- Allow flexible configuration using environment variables.  
- Run inside containers with Docker or docker‑compose.

---

## Features

- User login / logout.  
- OAuth authentication with Google and GitHub.  
- Error handling for failed authentication attempts.  
- `.env` configuration example.  
- Dockerized for easy deployment.

---

## Requirements

- Python 3.x  
- pip / virtualenv  
- Node.js & npm/yarn
- Git  
- Docker & Docker Compose (for containerized deployment)  

---

## Project Structure

``` python
flask-app-authen/
│
├── backend/               # Backend source
├── frontend/              # Frontend source code
├── .env.example           # Example environment config file
├── docker-compose.yaml    # Orchestrates services using Docker
├── argocd-application.yaml # For init ArgoCD deployment
└── README.md
```

---

## Installation & Running

1. **Clone the repository**

   ```bash
   git clone https://github.com/khanhquoc4114/flask-app-authen.git
   cd flask-app-authen
   ```

2. **Setup backend environment**

   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Copy `.env.example` to `.env` and fill in your credentials:

   ``` python
   GOOGLE_CLIENT_ID=
   GOOGLE_CLIENT_SECRET=

   GITHUB_CLIENT_ID=
   GITHUB_CLIENT_SECRET=

   FLASK_SECRET_KEY=

   POSTGRES_DB=
   POSTGRES_USER=
   POSTGRES_PASSWORD=
   POSTGRES_HOST=
   ```

   Other variables as needed (callback URLs, host, port)

4. **Run the backend**

   ```bash
   flask run
   ```

   Or using your specific script (`python app.py` etc.).

5. **Setup frontend** (if required)  
   Inside the `frontend/` directory, run:

   ```bash
   npm install
   npm run build
   ```

   Or use `yarn` if preferred.

---

## Docker & Docker Compose

To run the application with Docker:

```bash
docker-compose up --build
```

This will build and run both backend and frontend services as defined in `docker-compose.yaml`.

---

## 🚀 Deployment

This application is deployed using the **GitOps** approach with GitHub Actions, Docker Hub, and ArgoCD.  
The CI/CD pipeline is defined in `.github/workflows/ci.yml`.

### CI/CD Workflow

1. **Build & Push Docker image**
   - When new code is merged into the `main` branch, GitHub Actions will:
     - Build the Docker image of the application.
     - Tag it as `:latest` and `:<commit-sha>`.
     - Push the image to Docker Hub (`your-dockerhub-username/flask-app-authen`).

2. **Update the manifest repository**
   - After pushing the image, the pipeline will:
     - Clone the manifest repo: [flask-authen-manifest](https://github.com/khanhquoc4114/flask-authen-manifest).
     - Update the `image` field in `deployment.yaml` with the new tag.
     - Commit and push the change back to the manifest repo.

3. **Deploy with ArgoCD**
   - ArgoCD is configured to track the [flask-authen-manifest](https://github.com/khanhquoc4114/flask-authen-manifest) repository.
   - Once the manifest is updated, ArgoCD will automatically:
     - Sync the application state.
     - Deploy the new Docker image version to the Kubernetes cluster.

### Required Secrets

In the source code repo (`flask-app-authen`), the following secrets must be configured in GitHub Actions:

- `DOCKERHUB_USERNAME` – Docker Hub username  
- `DOCKERHUB_TOKEN` – Docker Hub token  
- `GITHUB_TOKEN` – Personal Access Token with push permissions for the manifest repo

---

## Best Practices & Future Improvements

- **Disable debug mode** in production.  
- **User data persistence**: store users in a database instead of only session.  
- **Token refresh & expiration** handling.  
- **Security hardening**: rate limiting, CSRF protection, brute force defense.  
- **Automated testing**: unit tests & integration tests.  
- **CI/CD pipeline**: automated build, test, deploy.
