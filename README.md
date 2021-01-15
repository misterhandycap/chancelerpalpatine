# ChancelerPalpatine

I love democracy! And Python!

## Setup

### Installing dependencies

```bash
python3 -m virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Creating environment variables

```bash
cp .env.sample .env
nano .env
```

## Updating dependencies

```bash
pip3 freeze > requirements.txt
```

## Running database migrations

```bash
alembic upgrade head
```

## Running tests

```bash
python3 -m unittest discover -s tests/
```

## Creating new migrations

```bash
PYTHONPATH=$(pwd) alembic revision -m "MIGRATION_NAME"
```
