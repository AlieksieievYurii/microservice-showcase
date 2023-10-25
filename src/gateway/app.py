"""
Gateway service
"""

import json
import gridfs
import pika
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from auth_svc import access
from auth import validate
from storage import util


server = Flask(__name__)
mongo_video = PyMongo(server, uri="mongodb://mongodb:27017/videos")

mongo_mp3 = PyMongo(server, uri="mongodb://mongodb:27017/mp3s")

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    """
    Endpoint to perform authentication
    """
    token, err = access.login(request)

    if not err:
        return token

    return err


@server.route("/upload", methods=["POST"])
def upload():
    """
    Asynchromous endpoint for performing upload target video file
    """
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            err = util.upload(f, fs_videos, channel, access)

            if err:
                return err

        return "success!", 200
    else:
        return "not authorized", 401


@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)
    access = json.loads(access)
    
    if err:
        return err

    if access['admin']:
        fid_string = request.args.get('fid')

        if not fid_string:
            return "FID is required!"

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f'{fid_string}.mp3')
        except Exception as err:
            return f"Internal Server Error: {err}", 500

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
