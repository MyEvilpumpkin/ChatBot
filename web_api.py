from flask import Flask, render_template, request

from chatbot_api import chatbot_response

app = Flask(__name__)
app.static_folder = 'static'


def reformat_response(data):
    text = str(data[0])
    commands = data[1]
    if len(commands):
        text += "</div><div class=\"msg-commands\">"
        for command in commands:
            text += "<div class=\"msg-command\" onClick=\"cmdOnClick(this.innerText)\">" + str(command[0]) + "</div>"
    return text


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/getresponse")
def get_bot_response():
    user_text = request.args.get('msg')
    response = chatbot_response(user_text)
    return reformat_response(response)


@app.route("/getfirstmessage")
def get_first_bot_message():
    response = chatbot_response('Привет')
    first_response = ('Привет, я - Атом, бот-помощник!<br>Я помогу тебе освоиться в нашей компании<br>'
                      'Чем я могу помочь?', response[1])
    return reformat_response(first_response)


if __name__ == "__main__":
    app.run()
