import telebot
from telebot import types
from constants import PATH_TO_CONFIG
import flask
import configparser

config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG)

WEBHOOK_URL_BASE = "https://{}:{}".format(config['WEBHOOK']['host'], config['WEBHOOK']['port'])
WEBHOOK_URL_PATH = "/{}/".format(config['BOT']['token'])

bot = telebot.TeleBot(config['BOT']['token'], threaded = False)  # бесплатный аккаунт pythonanywhere запрещает работу с несколькими тредами

# удаляем предыдущие вебхуки, если они были
bot.remove_webhook()

# ставим новый вебхук = Слышь, если кто мне напишет, стукни сюда — url
bot.set_webhook(url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

@bot.message_handler(commands = ['start'])
def send_welcome(message):
	'''Function sends welcome message and adds a new user.

	:param message: Message object
	:return: nothing
	'''
	bot.send_message(message.chat.id, "Hello, {0}! I will be helping you until you learn to touch type. Gjt[fkb!"
		.format(message.from_user.first_name))

@bot.message_handler(commands = ['help'])
def provide_help(message):
	'''Function helps.

	:param message: Message object
	:return: nothing
	'''

	bot.send_message(message.chat.id, "Idk ask Masha")

@bot.message_handler(func = lambda message: True)
def echo_message(message):
	'''Function fixes layout of the replyed message (english to russian only).

	:param message: Message object
	:return: nothing
	'''
	print(message.text)

	res = change_layout(message.text)

	if res:
		bot.send_message(message.chat.id, res)
	else:
		bot.send_message(message.chat.id, "Can't decipher this")

@bot.inline_handler(func = lambda query: len(query.query) > 0)
def query_text(query):

	if isinstance(query.query, str):
		decoded = change_layout(query.query)

		r = types.InlineQueryResultArticle(
				id = '1', title = "Decoded",
				description = decoded,
				input_message_content = types.InputTextMessageContent(
				message_text = decoded))
	else:
		r = types.InlineQueryResultArticle(
				id = '1', title = "Error")

	bot.answer_inline_query(query.id, [r])

def change_layout(text):
	'''Function fixes layout of the text (english to russian only).

	:param text: string
	:return: new string
	'''

	l = []

	rus_keyboard = "йцукенгшщзхъфывапролджэячсмитьбю. ё1234567890-="
	en_keyboard = "qwertyuiop[]asdfghjkl;'zxcvbnm,./ `1234567890-="

	for i in text:
		for j in range(len(en_keyboard)):
			if (i == en_keyboard[j]):
				l.append(rus_keyboard[j])
			else:
				l.append(i)

	return ''.join(l)

# пустая главная страничка для проверки
@app.route('/', methods = ['GET', 'HEAD'])
def index():
    return 'ok'


# обрабатываем вызовы вебхука = функция, которая запускается, когда к нам постучался телеграм 
@app.route(WEBHOOK_URL_PATH, methods = ['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


bot.polling()