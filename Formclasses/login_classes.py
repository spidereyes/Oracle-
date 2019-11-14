from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message="用户名不可为空")])
    password = PasswordField("Password", render_kw={'class':'text-input', 'id':'pword'},
                             validators=[Length(min=4, max=18, message="长度为4到18"), DataRequired(message="密码不可为空")])
    captcha = StringField("Catpcha", render_kw={'class':"text-input", 'id':'catpcha'},
                          validators=[DataRequired(message="验证码不可为空")])
    check = BooleanField("Check", render_kw={'id':"remember-input"})
    submit = SubmitField("Submit", render_kw={'class':"login-button"})

class ModifyForm(FlaskForm):
    username = StringField("Username", render_kw={'class':'text-input', 'id':'uname'},
                           validators=[DataRequired(message="用户名不可为空")])
    oldpassword = PasswordField("oPassword", render_kw={'class':'text-input', 'id':'pword', 'placeholder':'密码长度为4到18个字符'},
                                validators=[Length(min=4, max=18, message="长度为4到18"), DataRequired(message="密码不可为空")])
    newpassword = PasswordField("nPassword", render_kw={'class':'text-input', 'id':'nword', 'placeholder':'密码长度为4到18个字符'},
                                validators=[Length(min=4, max=18, message="长度为4到18"), DataRequired(message="密码不可为空")])
    confirmpassword = PasswordField("cPassword", render_kw={'class':'text-input', 'id':'confirmpword'},
                                    validators=[Length(min=4, max=18, message="长度为4到18"), DataRequired(message="密码不可为空")])
    submit = SubmitField("Submit", render_kw={'class':"login-button", 'value':"提交"})
