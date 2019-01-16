#!/usr/bin/env python
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit, disconnect
from forms import LoginForm

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)


def get_true_message(message):
    """
    Linux 需转换字符格式，否则乱码
    """
    str = message.encode('raw_unicode_escape')
    return str.decode('utf-8')

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    获取登录用户名并跳转
    """
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        return redirect(url_for('chat'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
    return render_template('login.html', form=form)

@app.route('/chat')
def chat():
    """
    聊天主界面
    """
    name = session.get('name', '')
    if name == '':
        return redirect(url_for('/'))
    return render_template('index.html', name=name)

@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    """
    广播信息
    """
    data = get_true_message(message['data'])
    data = message['data'] 
    # data = get_true_message(data) #线上需启动
    print(data)
    emit('my_response',
         {'data': data, 'name':session['name']},
         broadcast=True)

@socketio.on('rename', namespace='/test')
def rename(message):
    """
    重命名
    """
    old_name = session.get(request.sid, request.sid)
    data = message['data'] 
    # data = get_true_message(data) #线上需启动
    session['name'] =data
    session[request.sid] = data
    emit('login', {'data': old_name + '已重命名!', 'name': session['name']},
         broadcast=True)

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    """
    下线断开链接，广播下线信息
    """
    name = session.get('name',request.sid)
    session.pop('name')
    session.pop(request.sid)
    emit('my_response',
         {'data': '已下线!', 'name':name},
                  broadcast=True)
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    """
    建立链接，广播上线信息
    """
    session['name'] = session.get('name', request.sid)
    session[request.sid] = session['name']
    emit('login', {'data': '已上线!', 'name': session['name']},
         broadcast=True)


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    # socketio.run(app, debug=True)
    socketio.run(app, host='0.0.0.0',debug=True)