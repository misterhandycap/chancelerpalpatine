# ChancelerPalpatine

I love democracy! And Python!

## Setup

Requirements:

- Python 3.10+

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

## Internationalization

Make sure to keep track of all your newly inserted messages when creating a new feature.
When adding new messages to the application, please update bot/i18n/base.pot file with the
newly inserted messages. After doing so, run the following from the project root directory:

```bash
bash bot/i18n/merge_pot_to_po.sh
```

Then add manually your changes to the language files you wish to translate. After translating, 
run the following, replacing `$LANGUAGE` to the language code you've just translated:

```bash
msgfmt -o bot/i18n/$LANGUAGE/LC_MESSAGES/base.mo bot/i18n/$LANGUAGE/LC_MESSAGES/base.po
```
