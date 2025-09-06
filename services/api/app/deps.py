from fastapi import Depends
from .db import get_db


def db_dep():
    return next(get_db())