# CloudNote - College Notes Sharing Platform

CloudNote is a modern, responsive, and secure cloud-inspired web application for college students to upload, search, filter, and download academic notes in **PDF** and **DOCX** formats.

Built with a production-grade stack including **Python Django**, **SQLite**, and **Bootstrap 5**, it supports full containerization with **Docker** and automated **CI/CD** pipelines ready for **AWS EC2** deployment.

---

## Features

1. **User Authentication**: Student registration and login forms using Django's built-in hashed session storage.
2. **Document Management**:
   - Upload notes with Title, Subject Category, and Descriptions.
   - Secure server-side download endpoint that increments tracking statistics.
3. **Interactive Search & Filtering**:
   - Live query searching across titles and descriptions.
   - Horizontal scrolling category pills for easy subject filters.
4. **Custom Admin Panel**: Dedicated moderation interface for system statistics and content moderation.
5. **Modern Premium Interface**:
   - Fully responsive design with glassmorphism card layouts.
   - Client-side validation for file formats and sizes (< 10MB).
   - Instant Light/Dark Mode toggle (saves settings in local storage).
   - Spinner loading animations during upload validation checks.
   - Auto-dismissing alerts.

---

## Folder Structure

Below is the clean professional layout of this codebase:

```
CloudNote/
│
├── cloudnote/              # Django Project configuration folder
│   ├── settings.py         # Main Django settings (DB, paths, routing, auth)
│   ├── urls.py             # Root URL routing registry
│   └── wsgi.py             # Web Server Gateway Interface (for Gunicorn)
│
├── notes/                  # Core Application app folder
│   ├── migrations/         # Auto-generated database migration scripts
│   ├── templates/          # HTML Templates layer
│   │   └── notes/
│   │       ├── base.html   # Main layout shell with navbar, footer and alerts
│   │       ├── index.html  # Landing catalog list with search & category pills
│   │       ├── login.html  # Student login card
│   │       ├── register.html # Student registration card
│   │       ├── profile.html # User personal files history and quick upload button
│   │       └── admin_dashboard.html # Force delete moderation panel for staff
│   ├── models.py           # Note SQL Database definitions
│   ├── urls.py             # App URL endpoints
│   └── views.py            # Route controller functions
│
├── static/                 # Static Assets (custom frontend layer)
│   ├── css/
│   │   └── style.css       # Premium style (glassmorphism, variables, dark mode)
│   └── js/
│       └── main.js         # UI logic (theme toggler, file validations, loading overlay)
│
├── media/
│   └── uploads/            # Local directory where uploaded notes are stored (gitignored)
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml       # GitHub Actions automated lint and container checks
│
├── manage.py               # Django local administration script
├── requirements.txt        # Python external dependencies list
├── Dockerfile              # Setup environment blueprint
├── docker-compose.yml      # Multi-container local execution mapping
├── .gitignore              # Config files, DB, and media assets exclude instructions
└── README.md               # User setup & deployment handbook
```

---

## Tech Stack

* **Backend**: Python Django (WSGI)
* **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons
* **Database**: SQLite (default relational DB)
* **WSGI Production Server**: Gunicorn
* **Containerization**: Docker & Docker Compose
* **CI/CD**: GitHub Actions

---

## Local Setup Instructions

### Prerequisites
* Python 3.10+ installed.
* Pip (Python Package Installer).

### 1. Clone the repository and navigate inside
```bash
git clone <repository_url> CloudNote
cd CloudNote
```

### 2. Create and activate a Virtual Environment (Optional but recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install packages
```bash
pip install -r requirements.txt
```

### 4. Create database and apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser / Administrator account
To access the admin dashboard panel, you must flag your account as staff:
```bash
python manage.py createsuperuser
```
Follow the prompts (Username, Email, Password) to complete registration.

### 6. Run the local development server
```bash
python manage.py runserver
```
Visit the platform in your browser at `http://127.0.0.1:8000`.

---

## Docker Deployment (Local or Staging)

### 1. Build and Run containers using Docker Compose
```bash
docker-compose up --build
```
This command automatically builds the Dockerfile, runs migrations, aggregates static assets, and boots Gunicorn on `http://localhost:8000`.

### 2. Run in detached background mode
```bash
docker-compose up -d
```

### 3. Stop containers
```bash
docker-compose down
```

---

## Production Deployment on AWS EC2

Here is a step-by-step guide to deploying CloudNote to an AWS EC2 instance:

### Step 1: Launch an AWS EC2 Instance
1. Log in to your **AWS Console**.
2. Navigate to **EC2 Dashboard** and click **Launch Instance**.
3. Choose **Ubuntu Server 22.04 LTS** (64-bit x86) as the AMI.
4. Select instance type `t2.micro` (free tier eligible).
5. Generate and download a key pair (`.pem` file) for SSH access.
6. Under **Network Settings / Security Group**:
   - Allow **SSH traffic** (Port 22) from your IP.
   - Allow **HTTP traffic** (Port 80) from anywhere.
   - Allow custom TCP **Port 8000** (if running Docker directly without reverse proxy).

### Step 2: Install Docker and Docker Compose on EC2
SSH into your instance and run the following command blocks:
```bash
# SSH connection
ssh -i "your-key.pem" ubuntu@ec2-your-instance-ip.compute-1.amazonaws.com

# Update package lists
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add Ubuntu user to Docker group
sudo usermod -aG docker ubuntu
# Log out and log back in to apply Docker user permissions
exit
```

### Step 3: Deploy Project Files
You can transfer files using Git:
```bash
# SSH back into EC2
ssh -i "your-key.pem" ubuntu@ec2-your-instance-ip.compute-1.amazonaws.com

# Clone the repository
git clone <your_github_repo_url>
cd CloudNote
```

### Step 4: Run Application in Production
1. Start the container:
   ```bash
   docker-compose up -d --build
   ```
2. Create your administrator account inside the container:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
3. Visit the website in your web browser at: `http://<your-ec2-public-ip>:8000`.

---

## Future Scope

For scaling up the deployment of CloudNote in the future, the following technologies should be integrated:

1. **Kubernetes Deployment**: Orchestrate microservices, enable auto-scaling, and support zero-downtime rolling updates using K8s manifests.
2. **AWS S3 Integration**: Re-route the Django `FileField` storage backend from local disk volumes to Amazon S3 buckets for high durability, lower latency downloads, and serverless asset handling.
3. **Monitoring & Alerting (Prometheus & Grafana)**: Hook up metrics scraping modules to visualize active student sessions, download speeds, and server resource health.
4. **Terraform (Infrastructure as Code)**: Write modular `.tf` scripts to automate provisioning of VPC networks, security groups, EC2 nodes, and RDS databases in seconds.
