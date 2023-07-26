from flask import Flask, request, render_template, abort
from bot import Bot
import os

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/twitter/webhook', methods=['POST', 'GET'])
def webhook():
    if (request.method == 'POST'):
        data = request.json
        if 'direct_message_events' in data:
            user_id = data['direct_message_events'][0]['message_create']['sender_id']
            msg_data = data['direct_message_events'][0]['message_create']['message_data']['text'].lower()

            bot = Bot(user_id)

            if 'oi' in msg_data:
                bot.dm('Olá!')

            if 'cachorro' in msg_data:
                bot.dog()

            if 'gato' in msg_data:
                bot.cat()

        return 'success', 200
    elif (request.method == 'GET'):
        crc_token = request.args.get('crc_token')

        bot = Bot()

        return bot.twt.crc_challenge(crc_token)
    else:
        abort(400)

#app.run(debug=True)
