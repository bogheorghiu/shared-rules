import os
import sqlite3

DEV_DB = os.path.join("data", "dev.db")


def connect(path=DEV_DB):
    return sqlite3.connect(path)
