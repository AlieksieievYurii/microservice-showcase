"""
This is authentication service
"""

import os
import datetime

from flask import Flask, request
from flask_mysqldb import MySQL
import jwt

server = Flask(__name__)
mysql = MySQL(server)

server.config["JWT_SECRET"] = os.environ.get("JWT_SECRET")

server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))


@server.route("/login", methods=["POST"])
def login():
    """
    Performs login process
    """

    if not request.authorization:
        return "missing credentials", 401

    cur = mysql.connection.cursor()

    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s",
        (request.authorization.username,),
    )

    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if (
            request.authorization.username != email
            or request.authorization.password != password
        ):
            return "invalid creadentials", 401

        return create_jwt(
            request.authorization.username, server.config["JWT_SECRET"], True
        )
    else:
        return "invalid credentials", 401


def create_jwt(email: str, secret: str, is_admin: bool):
    """Creates JWT"""
    return jwt.encode(
        {
            "username": email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": is_admin,
        },
        secret,
        algorithm="HS256",
    )


@server.route("/validate", methods=["POST"])
def validate():
    """Validates JWT"""
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, server.config["JWT_SECRET"], algorithms=["HS256"]
        )
    except:
        return "not athorized", 401


if __name__ == "__main__":
    # This is essential to set host to 0.0.0.0
    # if we want to make the server listen to external incoming requests
    server.run(host="0.0.0.0", port=5000)
