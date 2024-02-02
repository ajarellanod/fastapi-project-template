# Fastapi template
This project was inspired by [manage-fastapi](https://ycd.github.io/manage-fastapi/)! :tada:

## License

This project is licensed under the terms of the BSD license.

## How to start?

#### Requirements
- Pyenv or python >=3.11
- Docker and docker compose
- pip

#### Installation for local development
- Create virtualenv
    - Pyenv version `pyenv virtualenv 3.11 <project>`
    - Python version `python -m venv <project>`
- Activate virtualenv
    - Pyenv version `pyenv activate <project>`
    - Python version `source <dir/to/venv/bin>`
- Install dependencies `pip install -r dev-requirements.txt`
- Install pre-commit `pre-commit install`
- Run dev database `cd db && docker compose up -d`
- Config and rename .env_sample file to .env
- Run devserver `python devserver.py`


#### Migrations?
When you make some changes to app.models files and you want to apply those changes
you need to run alembic to detect those changes and apply to the database.

For this you'll need the dev database started because alembic need to check
the current state of all migrations. So, before run with docker you need to create
migrations.

How to do it?
- Init the dev db.
- Generate migrations files `alembic revision --autogenerate -m "<migration's name>"`
- Apply migrations `alembic upgrade head`
- Return to last migration if nedeed `alembic downgrade head`


#### Run with docker
- Create migrations (It is not necessary to apply migrations to the dev db)
- `docker compose up -d`
