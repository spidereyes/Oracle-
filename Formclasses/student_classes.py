from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, FileField
from wtforms.validators import Length, DataRequired, AnyOf, InputRequired, Email, Regexp

class SinforClass:
    def __init__(self, tuple1):
        self.__xh = tuple1[0]
        self.__xm = tuple1[1]
        self.__sex = tuple1[2]
        self.__dept = tuple1[3]
        self.__major = tuple1[4]
        self.__classnum = tuple1[5]
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

    def getclass(self):
        return self.__classnum

    def getcomedate(self):
        return self.__comedate

    def getimage(self):
        return self.__image

class DiaryandPost:
    def __init__(self, tuple2):
        self.__diary = tuple2[0]
        self.__apost = tuple2[1]
        self.__tpost = tuple2[2]

    def getdiary(self):
        return self.__diary

    def getapost(self):
        return self.__apost

    def gettpost(self):
        return self.__tpost

class StudentinforClass(FlaskForm):
    Xh = StringField("学号", render_kw={"id":"xh", "class":"simulate_input"})
    Xm = StringField("姓名", render_kw={"id":"xm", "class":"simulate_input", "placeholder":"所有字段不可为空"}, validators=[DataRequired()])
    Sex = StringField("性别", render_kw={"id":"sex", "class":"simulate_input", "placeholder":"只可输入男或女"}, validators=[DataRequired(), AnyOf(["男", "女"])])
    Mz = StringField("民族", render_kw={"id":"mz", "class":"simulate_input"}, validators=[DataRequired()])
    Id = StringField("身份证号", render_kw={"id":"mz", "class":"simulate_input", "placeholder":"中国大陆居民身份证"}, validators=[DataRequired(), Length(min=18, max=18)])
    Birthday = StringField("出生日期", render_kw={"id": "birthday", "class":"simulate_input", "placeholder":"yyyy.mm.dd的格式输入，中间以.分隔"},
                          validators=[DataRequired(), Regexp("^([0-9]{4})\.(1[0-2]|[1-9])\.(3[0-1]|[1-2][0-9]|[1-9])$")])
    Dept = StringField("学院", render_kw={"id": "dept", "class": "simulate_input"}, validators=[DataRequired()])
    Major = StringField("专业", render_kw={"id": "major", "class": "simulate_input"}, validators=[DataRequired()])
    Class = StringField("班号", render_kw={"id":"class", "class":"simulate_input"}, validators=[DataRequired()])
    Phone = StringField("联系电话", render_kw={"id": "phone", "class":"simulate_input"}, validators=[DataRequired()])
    Mail = StringField("邮箱", render_kw={"id": "mail", "class":"simulate_input"}, validators=[Email()])
    Type = StringField("学生类别", render_kw={"id": "type", "class": "simulate_input"}, validators=[DataRequired()])
    Comedate = StringField("入学时间", render_kw={"id": "comedate", "class":"simulate_input", "placeholder":"yyyy.mm.dd的格式输入，中间以.分隔"},
                          validators=[DataRequired(), Regexp("^([0-9]{4})\.(1[0-2]|[1-9])\.(3[0-1]|[1-2][0-9]|[1-9])$")])
    Years = IntegerField("学制", render_kw={"id": "years", "class":"simulate_input", "placeholder":"只可为整数"}, validators=[InputRequired()])
    Address = StringField("家庭地址", render_kw={"id": "address", "class":"simulate_input"}, validators=[DataRequired()])

    Domitory = StringField("宿舍位置", render_kw={"id": "domitory", "class":"simulate_input"}, validators=[DataRequired()])
    Avatar = FileField("avatar", render_kw={"id": "pic_load", "accept":"image/gif, image/jpeg, image/png, image/jpg"})
    Submit = SubmitField("submit", render_kw={"value":"提交", "style":"margin-right: 30px"})