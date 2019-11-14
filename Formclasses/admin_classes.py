from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FileField, TextAreaField
from wtforms.validators import  DataRequired, AnyOf, Email, Regexp, Length

class AinforClass:
    def __init__(self, tuple1):
        self.__xh = tuple1[0]
        self.__xm = tuple1[1]
        self.__sex = tuple1[2]
        self.__dept = tuple1[3]
        self.__major = tuple1[4]
        self.__job = tuple1[5]
        self.__comedate = tuple1[6]
        self.__image = tuple1[7]

    def getxh(self):
        return self.__xh

    def getxm(self):
        return self.__xm

    def getsex(self):
        return self.__sex

    def getdept(self):
        return self.__dept

    def getmajor(self):
        return self.__major

    def getjob(self):
        return self.__job

    def getcomedate(self):
        return self.__comedate

    def getimage(self):
        return self.__image

class DiaryandAdminPost:
    def __init__(self, tuple2):
        self.__diary = tuple2[0]
        self.__apost = tuple2[1]

    def getdiary(self):
        return self.__diary

    def getapost(self):
        return self.__apost

class UserManage:
    def __init__(self, tuple3):
        self.__xh = tuple3[0]
        self.__pwd = tuple3[1]
        self.__permission = tuple3[2]

    def getxh(self):
        return self.__xh

    def getpwd(self):
        return self.__pwd

    def getpermission(self):
        return self.__permission


class EmployeeinforClass(FlaskForm):
    Xh = StringField("学号", render_kw={"id": "xh", "class": "simulate_input"})
    Xm = StringField("姓名", render_kw={"id": "xm", "class": "simulate_input", "placeholder": "所有字段不可为空"},
                     validators=[DataRequired()])
    Mz = StringField("民族", render_kw={"id": "mz", "class": "simulate_input"}, validators=[DataRequired()])
    Sex = StringField("性别", render_kw={"id":"sex", "class":"simulate_input", "placeholder":"只可输入男或女"}, validators=[DataRequired(), AnyOf(["男", "女"])])
    Marry = StringField("婚姻情况", render_kw={"id":"marry", "class":'simulate_input', "placeholder":"已婚或未婚，可不填"}, validators=[AnyOf(["已婚", "未婚", ""])])
    Society = StringField("政治面貌", render_kw={"id": "society", "class":"simulate_input"}, validators=[DataRequired()])
    Id = StringField("身份证号", render_kw={"id":"mz", "class":"simulate_input", "placeholder":"中国大陆居民身份证"}, validators=[DataRequired(), Length(min=18, max=18)])
    Major = StringField("专业", render_kw={"id": "major", "class": "simulate_input"}, validators=[DataRequired()])
    Dept = StringField("学院", render_kw={"id": "dept", "class": "simulate_input"}, validators=[DataRequired()])
    Job = StringField("职称", render_kw={"id": "job", "class": "simulate_input"}, validators=[DataRequired()])
    Phone = StringField("联系电话", render_kw={"id": "phone", "class":"simulate_input"}, validators=[DataRequired()])
    Mail = StringField("邮箱", render_kw={"id": "mail", "class":"simulate_input"}, validators=[Email()])
    Comedate = StringField("入职时间", render_kw={"id": "comedate", "class":"simulate_input", "placeholder":"yyyy.mm.dd的格式输入，中间以.分隔"},
                          validators=[DataRequired(), Regexp("^([0-9]{4})\.(1[0-2]|[1-9])\.(3[0-1]|[1-2][0-9]|[1-9])$")])
    Address = StringField("家庭地址", render_kw={"id": "address", "class":"simulate_input"}, validators=[DataRequired()])
    Avatar = FileField("avatar", render_kw={"id": "pic_load", "accept":"image/gif, image/jpeg, image/png, image/jpg"})
    Submit = SubmitField("submit", render_kw={"value":"提交", "style":"margin-right: 30px"})

class PostClass(FlaskForm):
    Xh = StringField("来源：", render_kw={"class":"input_box", "placeholder":"公告发表人", "id": "postfrom"}, validators=[DataRequired()])
    Head = StringField("标题", render_kw={"placeholder":"标题", "id":"new_head"}, validators=[DataRequired()])
    Postcontent = TextAreaField("内容")
    Date = StringField("日期：", render_kw={"class":"input_box", "id":"date", "placeholder":"日期以.分隔"}, validators=[DataRequired(), Regexp("^([0-9]{4})\.(1[0-2]|0[1-9]|[1-9])\.(3[0-1]|[1-2][0-9]|0[1-9]|[1-9])$")])
    Submit = SubmitField("submit", render_kw={"class":"body_button", "id": "postsubmit", "value":"提交"})

