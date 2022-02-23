from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from chatbot_api import chatbot_response
from models import Users, Jobs
from __init__ import create_app, db

app = create_app()


def reformat_response(data):
    text = str(data[0])
    index = 0
    while True:
        start_index = text.find('<img', index)
        if start_index == -1:
            break
        else:
            end_index = text.find('>', start_index)
            if end_index != -1:
                text = text.replace(text[start_index:end_index + 1], '<a onclick="imgOnClick(this)">' +
                                    text[start_index:end_index + 1] + '</a>', 1)
                index = end_index
    text = text.replace('%salary', str(current_user.salary))
    text = text.replace('%bot_name', 'Атом')
    if text.find('%jobs') != -1:
        jobs = Jobs.query.filter_by(user_id=current_user.id)
        jobsstr = ''
        for job in jobs:
            jobsstr += '<li>' + job.text + '</li>'
        text = text.replace('%jobs', jobsstr)

    commands = data[1]
    if len(commands):
        text += '</div><div class="msg-commands">'
        for command in commands:
            text += '<div class="msg-command" onClick="cmdOnClick(this.innerText)">' + str(command[0]) + '</div>'
    return text


@app.route('/', methods=['GET'])
@login_required
def main():
    if current_user.photo is None:
        photo = url_for('static', filename='images/nophoto.jpg')
    else:
        photo = current_user.photo
    return render_template('main_page.html',
                           avatar=str(photo),
                           surname=str(current_user.surname),
                           name=str(current_user.name),
                           patronymic=str(current_user.patronymic),
                           department=str(current_user.department),
                           experience=str(current_user.experience),
                           version='Версия 0.50',
                           bot_name='Атом')


@app.route('/chatbot_response', methods=['GET'])
@login_required
def chatbot_response_web():
    user_text = request.args.get('msg')
    response = chatbot_response(user_text)
    return reformat_response(response)


@app.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    return render_template('login_page.html',
                           error=''
                           if request.args.get('em') is None
                           else 'Пользователь с таким сочетанием логин/пароль не существует')


@app.route('/session', methods=['POST', 'DELETE'])
def session():
    if request.method == 'POST':
        user_login = request.form.get('login')
        user_password = request.form.get('password')
        user = Users.query.filter_by(login=user_login, password=user_password).first()
        if not user:
            return redirect(url_for('login', em=True), code=303)
        login_user(user, remember=True)
        return redirect(url_for('main'), code=303)
    elif request.method == 'DELETE':
        logout_user()
        return redirect(url_for('login'), code=303)


@app.route('/quests_and_walkthroughs', methods=['GET'])
@login_required
def quests_and_walkthroughs():
    query = db.engine.execute('SELECT '
                           'Quests.id AS quest_id, '
                           'Quests.name AS quest_name, '
                           'Quests.description AS quest_description, '
                           'QuestWalkthrough.status AS quest_status, '
                           'QuestPartWalkthrough.id AS questPart_id, '
                           'QuestPartWalkthrough.name AS questPart_name, '
                           'QuestPartWalkthrough.text AS questPart_text, '
                           'QuestPartWalkthrough.status AS questPart_status '
                           'FROM '
                           'Quests INNER JOIN (SELECT '
                           'QuestPartWalkthrough.quest_id, '
                           'MIN(QuestPartWalkthrough.status) AS status '
                           'FROM '
                           '(SELECT '
                           'Quest_parts.quest_id, '
                           'IFNULL(UserWalkthrough.status, 0) AS status '
                           'FROM '
                           'Quest_parts '
                           'LEFT JOIN '
                           '(SELECT '
                           'Walkthrough.questpart_id, '
                           '1 AS status '
                           'FROM '
                           'Walkthrough '
                           'WHERE '
                           'Walkthrough.user_id = %user_id) AS UserWalkthrough '
                           'ON (Quest_parts.id = UserWalkthrough.questpart_id)) AS QuestPartWalkthrough '
                           'GROUP BY QuestPartWalkthrough.quest_id) AS QuestWalkthrough '
                           'ON (Quests.id = QuestWalkthrough.quest_id) '
                           'INNER JOIN (SELECT '
                           'Quest_parts.id, '
                           'Quest_parts.name, '
                           'Quest_parts.text, '
                           'Quest_parts.quest_id, '
                           'IFNULL(UserWalkthrough.status, 0) AS status '
                           'FROM '
                           'Quest_parts '
                           'LEFT JOIN '
                           '(SELECT '
                           'Walkthrough.questpart_id, '
                           '1 AS status '
                           'FROM '
                           'Walkthrough '
                           'WHERE '
                           'Walkthrough.user_id = %user_id) AS UserWalkthrough '
                           'ON (Quest_parts.id = UserWalkthrough.questpart_id)) AS QuestPartWalkthrough '
                           'ON (Quests.id = QuestPartWalkthrough.quest_id) '
                           'ORDER BY '
                           'Quests.id, '
                           'QuestPartWalkthrough.id'.replace('%user_id', str(current_user.id)))
    result = '{"quests":['
    quest_id = -1
    res = ''
    for row in query:
        if quest_id != row[0]:
            result += res
            if quest_id != -1:
                res = ']},'
            else:
                res = ''
            res += '{'
            res += '"id":"' + str(row[0]) + '",'
            res += '"name":"' + str(row[1]) + '",'
            res += '"description":"' + str(row[2]) + '",'
            res += '"status":"' + str(row[3]) + '",'
            res += '"parts":[{'
            quest_id = row[0]
        else:
            res += ',{'
        res += '"id":"' + str(row[4]) + '",'
        res += '"name":"' + str(row[5]) + '",'
        res += '"text":"' + str(row[6]) + '",'
        res += '"status":"' + str(row[7]) + '"'
        res += '}'
    result += res
    result += ']}]}'
    result = result.replace('\r', '').replace('\n', '').replace('\t', '')
    return result


@app.route('/service_worker.js', methods=['GET'])
def service_worker():
    return app.send_static_file('service_worker.js'), 200, {'Content-Type': 'text/javascript'}


if __name__ == '__main__':
    app.run(host='0.0.0.0')
