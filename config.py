import os
from flask import session

def check_role(required_role):
    """Cek apakah role user di session sesuai dengan required_role"""
    role = session.get('role')
    return role == required_role


DB_CONFIG = {
    'host': os.getenv("PGHOST", "maglev.proxy.rlwy.net"),
    'dbname': os.getenv("PGDATABASE", "railway"),
    'user': os.getenv("PGUSER", "postgres"),
    'password': os.getenv("PGPASSWORD", "JxlxNXWerXUEyNLkCgxgBlhSvXKMfNjo"),
    'port': os.getenv("PGPORT", 39316)
}

MAIL_SETTINGS = {
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": os.getenv("MAIL_USERNAME", "secrap7@gmail.com"),
    "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD", "APP_PASSWORD_KAMU"),
    "MAIL_DEFAULT_SENDER": os.getenv("MAIL_DEFAULT_SENDER", "secrap7@gmail.com"),
    "MAIL_TIMEOUT": 10,              # ⟵ penting: cegah hang lama
    "MAIL_SUPPRESS_SEND": False,     # set True kalau mau test tanpa kirim email
}
