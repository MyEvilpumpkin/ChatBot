from flask import Flask, render_template, request

from chatbot_api import chatbot_response

app = Flask(__name__)
app.static_folder = 'static'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/getresponse")
def get_bot_response():
    user_text = request.args.get('msg')
    return str(chatbot_response(user_text))


@app.route("/getfirstmessage")
def get_first_bot_message():
    return 'Привет, я - Атом, бот-помощник!<br>Я помогу тебе освоиться в нашей компании'


if __name__ == "__main__":
    app.run()
