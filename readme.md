# Hello App Engine (CI/CD)

This project demonstrates:

- GitHub → Cloud Build (Webhook)
- Cloud Build → App Engine deployment
- Secrets stored in Google Secret Manager
- Secrets injected as environment variables
- Custom service account for deployment

## Flow

GitHub push → Cloud Build → App Engine

## Secrets Used

- db-password → DB_PASSWORD
- api-key → API_KEY
