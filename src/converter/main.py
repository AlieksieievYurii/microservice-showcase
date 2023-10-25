import pika, sys, os, time, json, tempfile
from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs
import moviepy.editor

def convert(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message)
    tf = tempfile.NamedTemporaryFile()
    out = fs_videos.get(ObjectId(message['video_fid']))
    tf.write(out.read())
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()

    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    f = open(tf_path, 'rb')
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)

    message['mp3_fid'] = str(fid)
    try:
        channel.basic_publish(
            exchange='',
            routing_key=os.environ.get('MP3_QUEUE'),
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
    except Exception as err:
        fs_mp3s.delete(fid)
        return "failed to publish message"

def main() -> None:
    client = MongoClient("mongodb", 27017)
    db_videos = client.videos
    db_mp3s = client.mp3s

    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = convert(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get('VIDEO_QUEUE'),
        on_message_callback=callback
    )
    print("Waiting for messages...")
    channel.start_consuming()

if __name__ == '__main__':
    main()