import typer
from alembic.command import downgrade as alembic_downgrade
from alembic.command import revision as alembic_revision
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine

from core.configs import settings

migrate_cli = typer.Typer()

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

alembic_config = AlembicConfig("./alembic.ini")
alembic_config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)
alembic_config.set_main_option("script_location", "migration/")


@migrate_cli.command()
def generate():
    alembic_revision(config=alembic_config, autogenerate=True)


@migrate_cli.command()
def upgrade():
    alembic_upgrade(alembic_config, "heads")


@migrate_cli.command()
def downgrade():
    alembic_downgrade(config=alembic_config, revision="-1")
