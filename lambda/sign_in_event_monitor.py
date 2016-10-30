# -*- encoding:utf-8 -*-

import json
import commands
import urllib
import boto3
import base64

WEB_HOOK_URL_ENCRYPTED = 'your_encrypted_web_hook_url'
CHANNEL = 'your_channel'


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    message = create_message(event['detail'])

    web_hook_url = get_web_hook_url(WEB_HOOK_URL_ENCRYPTED)
    return notify(message, CHANNEL, web_hook_url)


def create_message(detail):
    user_name = get_user_name(detail['userIdentity'])
    event_time = detail['eventTime']
    event_name = detail['eventName']
    event_result = detail['responseElements'][event_name]

    message = "AWS console sign in.\n" \
              + "UserName : " + user_name + "\n" \
              + "EventName : " + event_name + "\n" \
              + "EventResult : " + event_result + "\n" \
              + "EventTime : " + event_time
    return message


def get_user_name(user_identity):
    if user_identity['type'] == 'Root':
        return 'root'
    elif user_identity['type'] == 'IAMUser':
        return user_identity['userName']
    else:
        return json.dumps(user_identity)


def get_web_hook_url(web_hook_url_encrypted):
    return 'https:' + decrypt(web_hook_url_encrypted)


def decrypt(encrypted):
    return boto3.client('kms').decrypt(CiphertextBlob=base64.b64decode(encrypted))['Plaintext']


def notify(message, channel, web_hook_url):
    payload = {
        "text": message,
        "channel": channel,
        "username": "AWS Account Bot",
        "icon_emoji": ":ghost:"
    }
    escaped_payload = urllib.quote_plus(json.dumps(payload).encode('utf-8'))
    curl_command = 'curl -s -X POST -d "payload=%s" %s' % (escaped_payload, web_hook_url)
    return commands.getoutput(curl_command)
