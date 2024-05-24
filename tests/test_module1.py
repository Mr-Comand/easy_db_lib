# tests/test_module1.py
from datetime import datetime
from .config import *
from ..easy_db_lib import Database, Table

db = Database(
        host=DB_HOST, database=DB_DATABASE, user=DB_USER, password=DB_PASSWORD # noqa: F405
)
host = Table(db=db, createIfNotExists=True,structure={
        "name": "Host",
        "columns": {
            "host": {
                "type": {
                    "sql": "VARCHAR(255)",
                    "python": str
                },
                "primary": True,
                "not_null": True,
                "default": None,
                "unique": False,
                "check": None,
                "other": ""
            },
            "rescaninterval": {
                "type": {
                    "sql": "INTEGER",
                    "python": int
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "other": ""
            },
            "ignore": {
                "type": {
                    "sql": "BOOLEAN",
                    "python": bool
                },
                "primary": False,
                "not_null": True,
                #TODO: Config
                "default": False,
                "unique": False,
                "check": None,
                "other": ""
            }
        }
    })
page=Table(db=db, createIfNotExists=True,structure={
        "name": "Page",
        "columns": {
            "ID": {
                "type": {
                    "sql": "SERIAL",
                    "python": int
                },
                "primary": True,
                "not_null": True,
                "unique": False,
                "check": None,
                "other": ""
            },
            "Path": {
                "type": {
                    "sql": "VARCHAR(255)",
                    "python": str
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "other": ""
            },
            "Host": {
                "type": {
                    "sql": "VARCHAR(255)",
                    "python": str
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "references": {"table": host, "column": "host"},
                "other": ""
            },
            "last_scan": {
                "type": {
                    "sql": "TIMESTAMP",
                    "python": datetime
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "other": ""
            },
            "protocol": {
                "type": {
                    "sql": "VARCHAR(10)",
                    "python": str
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "other": ""
            }
        }
    })
links=Table(db=db, createIfNotExists=True,structure={
        "name": "Links",
        "columns": {
            "ID": {
                "type": {
                    "sql": "SERIAL",
                    "python": int
                },
                "primary": True,
                "not_null": True,
                "unique": False,
                "check": None,
                "other": ""
            },
            "Title": {
                "type": {
                    "sql": "VARCHAR(255)",
                    "python": str
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "other": ""
            },
            "Page_ID": {
                "type": {
                    "sql": "INTEGER",
                    "python": int
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "references": {"table": page, "column": "ID"},
                "other": ""
            },
            "Referring_To": {
                "type": {
                    "sql": "INTEGER",
                    "python": int
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "references":  {"table": page, "column": "ID"},
                "other": ""
            },
            "deleted": {
                "type": {
                    "sql": "BOOLEAN",
                    "python": bool
                },
                "primary": False,
                "not_null": True,
                "default": False,
                "unique": False,
                "check": None,
                "other": ""
            }
        }
    })
status=Table(db=db, createIfNotExists=True,structure={
        "name": "Status",
        "columns": {
            "ID": {
                "type": {
                    "sql": "SERIAL",
                    "python": int
                },
                "primary": True,
                "not_null": True,
                "unique": False,
                "check": None,
                "other": ""
            },
            "Timestamp": {
                "type": {
                    "sql": "TIMESTAMP",
                    "python": datetime  # Or  if you prefer
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "other": ""
            },
            "Link_ID": {
                "type": {
                    "sql": "INTEGER",
                    "python": int
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "references": {"table": links, "column": "ID"},
                "other": ""
            },
            "http_code": {
                "type": {
                    "sql": "INTEGER",
                    "python": int
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "other": ""
            },
            "changes": {
                "type": {
                    "sql": "JSON",
                    "python": dict
                },
                "primary": False,
                "not_null": False,
                "default": None,
                "unique": False,
                "check": None,
                "other": ""
            }
        }
    })

if False:
    host.delete(type="CASCADE")
    page.delete(type="CASCADE")
    links.delete(type="CASCADE")
    status.delete(type="CASCADE")

db.execute("""
DELETE FROM page;
DELETE FROM links;
DELETE FROM status;
DELETE FROM host;""")
el = host.table_element(toBeCreated=True)
el.host = "8.8.8.8"
el3 = host.table_element(toBeCreated=True)
el3.host = "1.1.1.1"
el2 = page.table_element(toBeCreated=True)
el2.Host = "8.8.8.8"
el2.delete()
el.delete()
print(el)
el.create()
el2.create()
el3.create()
print(el)
el.pull()
el2.pull()
print("-------")
print(el)
print(el2)
print(el2.Host_link)
el2.Host_link.rescaninterval = 1
print(el2.Host_link)
print(el)
el.pull()
print(el)
print("------")
for i in host.getAllWhere("Host ='1.1.1.1'"):
    print(i)