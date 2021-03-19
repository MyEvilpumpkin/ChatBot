from flask import Flask, render_template, request

from chatbot_api import chatbot_response

app = Flask(__name__)
app.static_folder = 'static'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    return str(chatbot_response(user_text)).encode('utf-8')


if __name__ == "__main__":
    app.run()
