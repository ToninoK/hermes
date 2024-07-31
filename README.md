# Hermes
Report delivery system concept. Consists of:

- API written in Flask
- Astronomer (Airflow) - Local deployment
- Kafka - Managed instance

## Local development

### API

In the root run:

```bash
docker compose build
```
NOTE: Environment required. Follow `.env_example`

After the command is done running, you can run the project using the following command:

```bash
docker compose up
```

This will start-up the API, a Redis container, and a Celery worker and scheduler.

### Airflow

To start up airflow [install the Astronomer CLI](https://www.astronomer.io/docs/astro/cli/overview) and run the following command (from root folder):

```bash
cd airflow && astro dev start
```
