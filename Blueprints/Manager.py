from flask import Blueprint, views, current_app, session, render_template, jsonify, \
    redirect, url_for, send_from_directory, make_response, request
from datetime import timedelta, datetime
from Formclasses.login_classes import LoginForm, ModifyForm
from Formclasses.admin_classes import PostClass
import random

Loginbp = Blueprint("login", __name__)
class Login(views.View):
    def __init__(self):
        self.Captcha_map = ['9192', '7234', '3645', '6962', '4134', '7309', '2021', '7209', '2857', '8863',
                       '9011', '4831', '2706', '5104', '6536', '9862', '5040', '6761', '5712', '3209']
        self.Form = LoginForm()
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()
    def dispatch_request(self):
        form = self.Form
        captcha_map = self.Captcha_map
        self.Cursor.execute('select xh from admin_')
        usernames = self.Cursor.fetchall()
        print(self.Form.data)
        if form.validate_on_submit(): # 同时验证请求类型和验证器的结果
            if form.captcha.data == captcha_map[session["captcha"] - 1]: # 验证验证码
                if (form.username.data,) in usernames: # 验证账号是否存在
                    self.Cursor.execute('select pwd from admin_ where xh = :s', [form.username.data]) # 账号存在再获取当前账号的密码
                    password = self.Cursor.fetchone()[0]
                    if form.password.data == password: # 验证密码正确性
                        if form.check.data == True: # 是否记住用户
                            session["user"] = form.username.data
                            session.permanent = True
                        else:
                            session["user"] = form.username.data
                        return redirect("index")
                    else:
                        seed = random.randint(1, 20)
                        session["captcha"] = seed
                        form.captcha.data = form.username.data = form.password.data = ""
                        return render_template("login.html", form=form, picseed=seed, error_msg="输入的账号或密码错误")
                else:
                    seed = random.randint(1, 20)
                    session["captcha"] = seed
                    form.captcha.data = form.username.data = form.password.data = ""
                    return render_template("login.html", form=form, picseed=seed, error_msg="输入账号错误")
            else:
                seed = random.randint(1, 20)
                session["captcha"] = seed
                form.password.data = ""
                form.captcha.data = ""
                return render_template("login.html", form=form, picseed=seed, error_msg="输入的验证码错误")
        else: # get请求直接改图上session
            if session.get("user"): # 有session直接进
                return redirect("index")
            else:
                seed = random.randint(1, 20)
                session["captcha"] = seed
                if request.cookies.get("redirect_msg"):
                    return render_template("login.html", form=form, picseed=seed, error_msg=request.cookies.get("redirect_msg"))
                else:
                    return render_template("login.html", form=form, picseed=seed, error_msg=None)

    def __del__(self):
        self.Cursor.close()
        self.DB.close()
        del self.Form

# 处理无需事先登录及登录后修改密码界面
class Modifypwd(views.View):
    def __init__(self):
        self.DB=current_app.config["DATABASE"].connection()
        self.Cursor=self.DB.cursor()
        self.Form = ModifyForm()
    def dispatch_request(self):
        if session.get('user'): # 登陆成功后修改密码为ajax请求
            opwd = request.form.get("oldpwd")
            npwd = request.form.get("newpwd")
            cpwd = request.form.get("confirmpwd")
            if len(npwd) > 3 and len(npwd) <= 18 and cpwd == npwd and len(opwd) > 3 and len(opwd) <= 18:
                self.Cursor.execute("select pwd from admin_ where xh = :s", [session["user"]])
                if self.Cursor.fetchone()[0] == opwd:
                    try:
                        if request.form.get("proxy") == "True": # 具有代理表示此时登录的为管理员并且试图修改查询字符串中的学号的密码
                            self.Cursor.execute("update admin_ set pwd = :s where xh = :s", [npwd, request.form.get("user")])
                        else: # 没有代理说明此用户想改自己密码
                            self.Cursor.execute("update admin_ set pwd = :s where xh = :s", [npwd, session["user"]])
                        self.DB.commit()
                    except:
                        self.DB.rollback()
                        return "系统繁忙，请稍后重试！"
                    else:
                        return "修改成功！即将关闭..."
                else:
                    return "原密码有误"
            else:
                return "密码格式有误（4至18）！"
        else: # 未登录时需要原密码和用户名，且分有get和post两种
            form = self.Form
            if request.method == "POST": # 判断请求方式
                if form.validate_on_submit(): # 判断表单情况
                    try: # 根据表单学号获取密码
                        self.Cursor.execute("select pwd from admin_ where xh = :s", [form.username.data])
                    except: # 用学号查不到密码证明学号不存在出现异常
                        form.newpassword.data = form.confirmpassword.data = form.oldpassword.data = form.username.data = ""
                        return render_template("modifypwd.html", msg="账号或密码出现错误", form=form)
                    else: # sql未出现异常
                        query_result = self.Cursor.fetchone()[0]
                        if query_result == form.oldpassword.data: # 先判断密码正误
                            if form.newpassword.data != form.confirmpassword.data or \
                                len(form.newpassword.data) > 18 or len(form.newpassword.data) < 4 or \
                                    len(form.confirmpassword.data) > 18 or len(form.confirmpassword.data) < 4: # 再判断两次输入长度是否不合理或不相同
                                form.newpassword.data = form.confirmpassword.data = form.oldpassword.data = ""
                                return render_template("modifypwd.html", msg="新密码有误", form=form)
                            else: # 新密码很合理
                                try: # 更新，提防数据库层出现问题，使用try
                                    self.Cursor.execute("update admin_ set pwd=:password where xh=:xuehao",
                                                        {'password': form.newpassword.data, 'xuehao': form.username.data })
                                    self.DB.commit()
                                    return render_template("modifypwd.html", msg="修改成功，即将跳转登陆界面", right="√", form=form, jsfile="js/autoredirect.js")
                                except:
                                    self.DB.rollback()
                                    return render_template("modifypwd.html", msg="系统繁忙，请稍后重试！", form=form)
                        else: # 密码与账号不匹配
                            return render_template("modifypwd.html", msg="账号或密码出现错误", form=form)
                else: # 表单验证器异常
                    return render_template("modifypwd.html", form=form, msg="提交失败，请重试")
            else:
                return render_template("modifypwd.html", form=form)

    def __del__(self):
        self.Cursor.close()
        self.DB.close()

class GetPost(views.View):
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()
        self.Form = PostClass()

    def dispatch_request(self):
        if session.get("user"):
            result = self.Cursor.execute("select identity from admin_ where xh = :s", [session["user"]]).fetchone()[0]
            if result == 0:
                return redirect("/admin/system")
            else:
                if request.method == "GET":
                    self.Cursor.execute("select xh, head, postdate from admin_post")
                    result = self.Cursor.fetchall()
                    posts = list() # 所有公告，结构：[[],[],[]...]
                    for i in result:
                        string = ""
                        adminpost = list()
                        adminpost.append(i[0])
                        adminpost.append(i[1])
                        adminpost.append("系统公告")
                        adminpost.append(toNormal(i[2], "third"))
                        for i in toNormal(i[2], "third").split("."):
                            string += i
                        adminpost.append(string)
                        posts.append(adminpost)
                    return render_template("admin_setting.html", identity="student", posts=posts, postform=self.Form, name=session["user"])
                else:
                    DB = current_app.config["DATABASE"].connection()
                    cursor = DB.cursor()
                    xh = request.form["xh"]
                    time = request.form["time"]
                    date = ""
                    timelist = time.split(".")
                    date += timelist[0]
                    date += "#"
                    if len(timelist[1]) == 1:
                        date += "0"
                        date += timelist[1]
                    else:
                        date += timelist[1]
                    date += "#"
                    if len(timelist[2]) == 1:
                        date += "0"
                        date += timelist[2]
                    else:
                        date += timelist[2]
                    try:
                        cursor.execute("select txtpath from admin_post where xh = :s and postdate = :s", [xh, date])
                        txtpath = cursor.fetchone()
                        normaldate = toNormal(date, "third")  # 从以#分隔变为以点分隔
                        try:
                            with open(current_app.config["DOWNLOADPATHP"] + "//" + txtpath[0], "r",
                                      encoding="utf-8") as file:
                                content = file.read()
                        except:
                            content = ""
                        return jsonify({"msg": "success", "content": content, "date": normaldate})
                    except:
                        return jsonify({"msg": "failed"})
        else:
            return redirect("/errormsg/1")
'''
一系列特殊界面：
1、主页依据权限路由给予
2、错误界面
3、下发文件
4、登出
5、介绍界面
'''
@Loginbp.route("/index", methods=["GET"])
def Index():
    if session.get("user"):
        db = current_app.config["DATABASE"].connection()
        Cursor = db.cursor()
        Cursor.execute("select identity from admin_ where xh = :s", [session["user"]])  # 密码正确验证身份选择重定向的路由
        identity = Cursor.fetchone()[0]
        if identity == 1:  # 按身份给路由
            return redirect("student/index?xh={}".format(session["user"]))
        elif identity == 2:
            return redirect("teacher/index?xh={}".format(session["user"]))
        else:
            return redirect("admin/index?xh={}".format(session["user"]))
    else:
        return redirect(url_for("Login"))

# 返回错误原因，errorcode: 1为权限不足，2为未输入账号, 3为404, 4为405
@Loginbp.route("/errormsg/<errorcode>", methods=["GET", "POST"])
def Error(errorcode):
    if request.method == "GET":
        if session.get("user"):
            cursor = current_app.config["DATABASE"].connection().cursor()
            cursor.execute("select identity from admin_ where xh = :s", [session["user"]])
            identity = cursor.fetchone()[0]
            if identity == 1:
                cursor.execute("select xm from student_infor where xh = :s", [session["user"]])
            else:
                cursor.execute("select xm from employee_infor where xh = :s", [session["user"]])
            name = cursor.fetchone()[0]
            if errorcode == '1':
                return render_template("error.html", name=getnamestr(name, identity), msg='抱歉！您的权限不足')
            elif errorcode == '2':
                return render_template("error.html", name=getnamestr(name, identity), msg='抱歉！您未输入账号')
            elif errorcode == '3':
                return render_template("error.html", name=getnamestr(name, identity), msg="抱歉！404资源未找到")
            elif errorcode == '4':
                return render_template("error.html", name=getnamestr(name, identity), msg="抱歉！405请求方式不当")
            elif errorcode == '5':
                return render_template("error.html", name=getnamestr(name, identity), msg="抱歉！请先向管理员申请")
            else:
                return render_template("error.html", name=getnamestr(name, identity), msg="别调皮不输入参数哦~~")
        else:
            response = make_response(redirect("/"))
            response.set_cookie("redirect_msg", "访问该url必须先进行登录", expires=datetime.now() + timedelta(seconds=2) - timedelta(hours=8), path="/")
            return response
    else:
        return redirect("/errormsg/4")

# 从uploads文件夹中下发文件
@Loginbp.route("/download/<type>/<filename>", methods=["GET", "POST"])
def Download(type, filename):
    if request.method == "GET":
        try:
            if type == "student":
                return send_from_directory(current_app.config["DOWNLOADPATHS"], filename=filename)
            elif type == "teacher":
                return send_from_directory(current_app.config["DOWNLOADPATHT"], filename=filename)
            elif type == "admin":
                return send_from_directory(current_app.config["DOWNLOADPATHA"], filename=filename)
            elif type == "default":
                return send_from_directory(current_app.config["DEFAULTPIC"], filename=filename)
            else:
                return redirect("/errormsg/3")
        except:
            return redirect("/errormsg/3")
    else:
        return redirect("/errormsg/4")

# 登出
@Loginbp.route("/logout", methods=["GET", "POST"])
def Logout():
    if request.method == "GET":
        session.pop("user")
        return redirect("/")
    else:
        return redirect("/errormsg/4")

# 介绍界面，无需登录只接get
@Loginbp.route("/introduction", methods=["GET", "POST"])
def Intro():
    if request.method == "GET":
        if session.get("user"):
            cursor = current_app.config["DATABASE"].connection().cursor()
            cursor.execute("select identity from admin_ where xh = :s", [session["user"]])
            identity = cursor.fetchone()[0]
            if identity == 1:
                cursor.execute("select xm from student_infor where xh = :s", [session["user"]])
            else:
                cursor.execute("select xm from employee_infor where xh = :s", [session["user"]])
            name = cursor.fetchone()[0]
            return render_template("intro.html", message=getnamestr(name, identity))
        else:
            return render_template("intro.html", message="请先登录")
    else: # 错误请求方式
        return redirect("/errormsg/4")

# 根据用户名得到其姓名加权限
def getnamestr(name, identity):
    if identity == 0:
        name += "管理员"
    elif identity == 1:
        name += "同学"
    else:
        name += "教师 "
    return name

def toNormal(string, type):
    a = str()
    string_list = string.split("#")
    if type == "first":
        a += string_list[0]
        if len(string_list[1]) == 1:
            a += "#0" + string_list[1]
        else:
            a += "#" + string_list[1]
        if len(string_list[2]) == 1:
            a += "#0" + string_list[2]
        else:
            a += "#" + string_list[2]
    elif type == "second":
        a += string_list[0]
        a += "年"
        a += string_list[1]
        a += "月"
        a += string_list[2]
        a += "日"
    else:
        a += string_list[0]
        a += "."
        a += string_list[1]
        a += "."
        a += string_list[2]
    return a