
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    """Accepts a nickname"""
    name = StringField('用户名', [DataRequired('用户名必填！'), Length(min=6, max=20, message='用户名必须介于6-20字符！')])
    submit = SubmitField('登录')
