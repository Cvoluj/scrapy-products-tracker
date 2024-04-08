# Products Tracker

## Overview
Products Tracker is an advanced service designed for tracking and storing detailed product data across multiple online retailers. This tool is ideal for anyone needing insights into the price dynamics, availability, and other essential data points of products listed on platforms like Zoro, Quill, Costco, CustomInk, and Viking Direct UK.

## Key Features
- **Process Management:** Leverages pm2 for efficient process management, ensuring stability and scalability.
- **Flexible Configuration:** Easily configurable via environment variables or a `.env` file, allowing for quick adjustments and setup.
- **Scalability:** Designed with extensibility in mind, making it simple to add new spiders for additional websites.
- **Deployment Ready:** Comes with detailed deployment instructions for various environments, ensuring a smooth rollout to production.

## Installation Requirements
Before starting, ensure your system meets the following requirements:
- Python 3.11 or newer
- Poetry for Python dependency management
- Docker, for container management of MySQL and RabbitMQ
- Node.js, for running pm2

### Installation Steps
1. **Repository Setup:** Clone the repository to your local system.
2. **Environment Configuration:** Copy the `.env.example` file to `.env` and configure it according to your needs.
3. **Dependency Installation:** Inside `src/python/src`, run `poetry install` to install Python dependencies.
4. **Virtual Environment:** Activate the Poetry virtual environment using `poetry shell`.
5. **Scrapy:** Ensure Scrapy is available and working within the virtual environment.
6. **Docker Containers:** Utilize `docker-compose.yml` to start MySQL and RabbitMQ services.
7. **CSV Preparation:** Place your CSV files with categories or product links in the designated project directory.
8. **Process Management:** Use pm2 to start the tracking session, ensuring both category and product files are supported.

## Configuration Details
- **API Keys and IDs:** For each supported website, specific API keys and Application IDs must be configured to enable scraping.
- **Session Interval:** Defines the interval between scraping sessions to avoid excessive load on the target websites.
- **Storage Paths:** Specifies where the scraped data, including images and CSV files, will be stored.
- **Supported Domains:** A list of domains that the tracker is configured to scrape data from.

## CSV File Format
The tracker uses CSV files for input, specifying either category URLs or direct product links. An example format is provided to guide the preparation of these files.

## Deployment Procedure
Deployment involves a series of steps designed to automate the rollout process using GitLab CI/CD and Paramiko for SSH operations. Key aspects include:
- **CI/CD Variables:** Properly configuring GitLab CI variables for secure and efficient deployment.
- **Remote Server Preparation:** Setting up directories and permissions on the target server to accommodate the tracker.
- **Deployment Script:** A script that automates the deployment process, including code delivery, dependency management, and cleanup of older deployments.

### Deployment Quick Guide
1. **Environment Variable Setup:** Ensure all necessary environment variables are correctly configured in the `.env` file.
2. **CI/CD Configuration:** Set up CI/CD pipelines in GitLab, including runner connection and deployment branch specification.
3. **Server Setup:** Prepare the target server with necessary directories, permissions, and environment configurations.
4. **Monitor Deployments:** Automated deployments will trigger on commits to the specified branch, making deployment seamless and consistent.

This README aims to provide a concise yet comprehensive guide to setting up and deploying the Products Tracker. For further assistance, consult the detailed documentation or reach out to the development team.
