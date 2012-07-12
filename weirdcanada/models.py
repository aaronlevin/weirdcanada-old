# coding=utf-8

import datetime
import hashlib
import pusher
import S3
import os
import yaml
from flask import flash
from flask import session
from helpers import slug
from pymongo import Connection

class WCConfig(object):
    """This class contains configuration and secret key data.
    This data is stored in a file called `config.yaml`. 
    """
    with open( os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml'), 'r') as tmp_file:
        config = yaml.load(tmp_file).copy()

class PushMessage(object):
    """API wrapper for Pusher messageing service. 
    The channel is stored in the session cookie as 'message_channel'
    channel = False for users who are not logged in.
    channel = username for users who are logged in.

    Depending on the event, listening for messages is done in certain event names.
    - Listen to upload events: upload_event
    """
    app_id = WCConfig.config['pusher']['app_id']
    key = WCConfig.config['pusher']['key']
    secret = WCConfig.config['pusher']['secret']

    def __init__(self):
        self.p = pusher.Pusher(
            app_id = self.app_id,
            key = self.key,
            secret = self.secret
        )
        if session.has_key('psh'):
            self.channel = session['psh']
        else:
            self.channel = 'null'
        return None

    def trigger(self,event, data, socket_id=None):
        """ trigger an push event.
        data must be a dictionary
        """
        if socket_id is not None:
            self.p[self.channel].trigger(event, data, socket_id)
        else:
            self.p[self.channel].trigger(event, data)
        return None

    def send(self, message):
        self.trigger('message',{'payload':message})
        return True

class AWSWrapper(object):
    AWS_ACCESS_KEY_ID = WCConfig.config['amazon']['aws_access_key_id']
    AWS_SECRET_ACCESS_KEY = WCConfig.config['amazon']['aws_secret_access_key']
    BUCKET_NAME = 'weird_canada'
    aws_http = 'https://s3.amazonaws.com/weird_canada'

    def __init__(self):
        self.conn = S3.AWSAuthConnection(self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY)
    
    def put(self, data, folder, filename):
        """Wrapper for uploading files to AWS
        data must have a callable .read() and .content_type
        """
        self.conn.put(self.BUCKET_NAME, folder + '/' + filename, S3.S3Object(data.read()),{'x-amz-acl':'public-read', 'Content-Type':data.content_type})

class Mongo(object):
    host = 'mongodb://' + WCConfig.config['mongo']['user'] + ':' + WCConfig.config['mongo']['pass'] + '@ds031107.mongolab.com/weird'
    port = 31107
    database_name = 'weird'
    
    def __init__(self, collection):
        self.connection = Connection(self.host, self.port)
        self.database = self.connection[self.database_name]
        self.collection = self.database[collection]

class User(Mongo):

    def __init__(self):
        super(User,self).__init__(collection='user')

    def check_username_password_combo(self, username=None, password=None):
        tmp_user = self.collection.find_one({'username':username})
        if tmp_user:
            return password == tmp_user['password']
        else:
            return False

class Post(Mongo):

    def __init__(self):
        super(Post, self).__init__(collection='post')

    def insert_from_form(self, form):
        
        # Initialize return dictionary
        insert_dict = {}

        # Push messaging
        msg = PushMessage()
        
        
        # insert artist data 
        msg.send('Inserting Artist & Label Data')
        insert_dict['artists'] = []
        for artist in form.data['release']['artists']:
            insert_dict['artists'].append({
                'name':artist['name'],
                'url':artist['url'],
                'slug':slug(artist['name']),
                'geo':{
                    'city':{
                        'name':artist['geo']['city'],
                        'slug':slug(artist['geo']['city']),
                    },
                    'province':{
                        'name':artist['geo']['province'],
                        'slug':slug(artist['geo']['province']),
                    },
                    'country':{
                        'name':artist['geo']['country'],
                        'slug':slug(artist['geo']['country']),
                    },
                },
            })

        # insert label data
        insert_dict['labels'] = []
        for label in form.data['release']['labels']:
            insert_dict['labels'].append({
                'name':label['name'],
                'url':label['url'],
                'slug':slug(label['name']),
                'geo':{
                    'city':{
                        'name':label['geo']['city'],
                        'slug':slug(label['geo']['city']),
                    },
                    'province':{
                        'name':label['geo']['province'],
                        'slug':slug(label['geo']['province']),
                    },
                    'country':{
                        'name':label['geo']['country'],
                        'slug':slug(label['geo']['country']),
                    },
                },

            })

        # insert author data
        insert_dict['authors'] = []
        for author in form.data['authors']:
            insert_dict['authors'].append({
                'name':author,
                'slug':slug(author),
            })
        # Future work: grab author URL and info from author db.

        # Insert content data
        insert_dict['contents'] = []
        for content in form.data['contents']:
            insert_dict['contents'].append({
                'language':content['language'],
                'from_the':content['from_the'],
                'content':content['text'],
                })
        
        # Insert Left over meta data
        insert_dict['section'] = form.data['section']
        insert_dict['publish_date'] = datetime.datetime.combine(form.data['publish_date'].date(),datetime.time(6,30)),
        insert_dict['tags'] = []
        for tag in form.data['tags'].split(';'):
            insert_dict['tags'].append(tag)
        
        # initialize AWS connection
        aws = AWSWrapper()

        # Upload Tracks
        insert_dict['tracks'] = []
        for track in form.data['tracks']:
            # make sure file is not empty
            if track['mp3'].filename != '': 
                filename = 'Weird_Canada-' + str(form.data['publish_date'].date()) + '-' + slug(track['artist']) + '-' + slug(track['name']) + os.path.splitext(track['mp3'].filename)[1]
                msg.send('uploading ' + filename + ' to AWS...')
                aws.put(data=track['mp3'], folder='music', filename=filename)
                insert_dict['tracks'].append({
                    'name':track['name'],
                    'artist':track['artist'],
                    'url':aws.aws_http + '/music/' + filename,
                })

        # Upload Cover Scan
        insert_dict['images'] = {}
        filename = 'Weird_Canada-' + str(form.data['publish_date'].date()) + '-' + slug(os.path.splitext(form.data['release']['cover_scan']['image'].filename)[0]) + os.path.splitext(form.data['release']['cover_scan']['image'].filename)[1]
        msg.send('uploading cover scan... ' + filename)
        aws.put(data=form.data['release']['cover_scan']['image'], folder='images', filename=filename)
        insert_dict['images']['cover_scan']= {
            'one_liner':form.data['release']['cover_scan']['one_liner'],
            'description':form.data['release']['cover_scan']['description'],
            'url':aws.aws_http + '/images/' + filename,
            }
       
        # Uploading Support Images
        insert_dict['images']['support_images'] = []
        for index, support in enumerate(form.data['release']['support_images']):
            if support['image'].filename != '':
                filename = 'Weird_Canada-' + str(form.data['publish_date'].date()) + '-' + slug(os.path.splitext(support['image'].filename)[0]) + os.path.splitext(support['image'].filename)[1]
                msg.send('uploading support image ... ' + filename)
                aws.put(data=support['image'], folder='images', filename=filename)
                insert_dict['images']['support_images'].append({
                    'one_liner':support['one_liner'],
                    'description':support['description'],
                    'url':aws.aws_http + '/images/' + filename,
                })

        self.object_id = self.collection.insert(insert_dict)
        return self.object_id 


