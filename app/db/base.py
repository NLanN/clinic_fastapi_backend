# Import all the models, so that Base has them before being
# imported by Alembic
from db.base_model import BaseModel  # noqa
from models.item import Item  # noqa
from models.user import User  # noqa
from models.patient import Patient # noqa