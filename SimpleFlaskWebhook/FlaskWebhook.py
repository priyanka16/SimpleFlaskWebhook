import os
from datetime import datetime, timedelta
from flask import Flask, request, abort, jsonify

WEBHOOK_VERIFY_TOKEN = os.environ.get('WEBHOOK_VERIFY_TOKEN')

CLIENT_AUTH_TIMEOUT = 24 # in Hours
authorised_clients = {}

app = Flask(__name__)

def temp_token():
    import binascii
    temp_token = binascii.hexlify(os.urandom(24))
    return temp_token.decode('utf-8')

@app.route("/message_options", methods=['GET', 'POST'])
def message_options():
    if request.method == 'GET':
        verify_token = request.args.get('verify_token')
        if verify_token == WEBHOOK_VERIFY_TOKEN:
            authorised_clients[request.remote_addr] = datetime.now()
            return jsonify({'status':'success'}), 200
        else:
            return jsonify({'status':'bad token'}), 401
    elif request.method == 'POST':
        client = request.remote_addr2
        if client in authorised_clients:
            if datetime.now() - authorised_clients.get(client) > timedelta(hours=CLIENT_AUTH_TIMEOUT):
                authorised_clients.pop(client)
                return jsonify({'status':'authorisation timeout'}), 401
            else:
                print(request.json)
                return jsonify({'status':'success'}), 200
        else:
            return jsonify({'status':'not authorised'}), 401

    else:
        abort(400)

@app.route("/")
def myNewWebPage():
    return "This is just the start of the world"

if __name__ == '__main__':
    if WEBHOOK_VERIFY_TOKEN is None:
        print('WEBHOOK_VERIFY_TOKEN has not been set in the environment.\nGenerating random token...')
        token = temp_token()
        print('Token: %s' % token)
        WEBHOOK_VERIFY_TOKEN = token
    app.run()
