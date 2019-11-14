from flask import Blueprint, views, current_app, session, request, redirect, render_template, jsonify
from Formclasses.admin_classes import DiaryandAdminPost, AinforClass, UserManage, EmployeeinforClass, PostClass
import datetime
from .Manager import toNormal
import re
import random
import os

Adminbp = Blueprint("admin", __name__)


class AdminIndex(views.View): # 设计为root用户，权限最高可随意查看及修改各教师及学生的信息，且阻止所有教师和学生的访问
    '''
    处理逻辑：
    首先判断session中是否存在user，即是否为可以登陆的用户
    然后判断查询字符串中的xh是否与当前登陆的学号一致，查询字符串中没有内容则报告用户不存在
    最后用学号取出权限若为0则代表为管理员可进入，否则代表是普通用户更改路由试图越权
    总之，先session（必须登录先），接着xh必须存在且和session['user']必须相等，最后xh的权限必须为0
    '''
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()

    def check_identity(self):
        if request.args.get("xh"):  # 查询字符串中取学号
            xh = request.args.get("xh")
            if xh == session["user"]:  # 判断和当前登陆用户是否一致
                self.Cursor.execute("select identity from admin_ where xh = '%s'" % (xh))
                xh_identity = self.Cursor.fetchone()[0]
                if xh_identity == 0:  # 权限绝对不会查询不到，且权限为管理员才允许进入
                    return 1
                else:
                    return "/errormsg/1"
            else:
                return "/errormsg/1"
        else:  # 取不到学号
            return "/errormsg/2"

    def dispatch_request(self):
        if session.get("user"): # 来这必须session必须有user，必须先登陆于是牵扯到登陆者的权限问题
            if request.method == "GET":
                check_result = self.check_identity()
                if isinstance(self.check_identity(), str):
                    return redirect(check_result)
                else:
                    self.Cursor.execute("select head, postdate, xh from admin_post order by postdate desc")
                    result = self.Cursor.fetchall()
                    admin_posts = list()
                    for i in result:
                        admin_posts.append(
                            {"head": i[0], "time": toNormal(i[1], "second"), "xh": i[2]})  # 获取系统公告的标题和发布时间及发布人

                    today = datetime.date.today()  # 获取今天日期
                    user_date = session["user"] + str(today.year) + "#" + str(today.month) + "#" + str(today.day)
                    self.Cursor.execute("select txtpath from users_diary where xh = :s", [session["user"]])
                    if (user_date + ".txt",) in self.Cursor.fetchall():  # 返回本人当天日记内容前先找找有没有这个文件
                        with open(current_app.config["DOWNLOADPATHA"] + "\\" + toNormal(user_date, "first") + ".txt", "r",
                                  encoding="utf-8") as file:
                            content = file.read()
                    else:  # 找不到就返回空给content
                        content = ""
                    dpform = DiaryandAdminPost((content, admin_posts))  # 该对象包括公告信息

                    self.Cursor.execute("select xh, xm, sex, dept, major, job, comedate, image from employee_infor where xh = :s",[session["user"]])
                    infor = self.Cursor.fetchone()
                    sinfor = AinforClass(infor)  # 造studentinformation对象，包含用户部分基本信息

                    return render_template("index.html", name=session["user"], identity="admin", proxy="", dpform=dpform, basic_infor=sinfor)
            else:
                return redirect("/errormsg/4")
        else:
            return redirect("/errormsg/1")

    def __del__(self):
        self.Cursor.close()
        self.DB.close()


class AdminSystem(views.View):
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()
        self.get = AdminUsers()
        self.Form = PostClass()

    def toSpecial(self, string):
        newstring = ""
        strlist = string.split(".")
        if len(strlist[0]) == 1:
            newstring += "0"
            newstring += strlist[0]
        else:
            newstring += strlist[0]
        newstring += "#"
        if len(strlist[1]) == 1:
            newstring += "0"
            newstring += strlist[1]
        else:
            newstring += strlist[1]
        newstring += "#"
        if len(strlist[2]) == 1:
            newstring += "0"
            newstring += strlist[2]
        else:
            newstring += strlist[2]
        return newstring

    def dispatch_request(self):
        if session.get("user"):
            check_result = self.get.noquery_check_identity()
            if isinstance(check_result, str):
                return redirect(check_result)
            else:
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
                # self.Cursor.execute("select xh, head, to_char(kh, '000000') from teacher_post")
                # result = self.Cursor.fetchall()
                # for i in result:
                #     teacherpost = list()
                #     teacherpost.append(i[0])
                #     teacherpost.append(i[1])
                #     teacherpost.append("课程公告")
                #     teacherpost.append(i[2])
                #     posts.append(teacherpost)
                self.Cursor.execute(
                    "select admin_.xh, identity from admin_, modify_infor_permission where admin_.xh = modify_infor_permission.xh and posted = 1")
                xh_identity = self.Cursor.fetchall()
                xh_identity_xm = list() # 所有修改信息申请，结构：[[],[],[]...]
                for i in xh_identity: # 通过identity决定查哪个表的xm
                    temp = list()
                    temp.append(i[0])
                    if i[1] == 1:
                        temp.append("学生")
                        self.Cursor.execute("select xm from student_infor where xh = :s", [i[0]])
                    else:
                        temp.append("教师")
                        self.Cursor.execute("select xm from employee_infor where xh = :s", [i[0]])
                    temp.append(self.Cursor.fetchone()[0])
                    xh_identity_xm.append(temp)
                if request.method == "GET":
                    return render_template("admin_setting.html", identity="admin", name=session["user"], proxy="", posts=posts,
                                           applies=xh_identity_xm, postform=self.Form)
                else: # post，首先要清楚主键为学号、发表时间二者复合主键
                    if self.Form.validate_on_submit():
                        xh = self.Form.Xh.data
                        head = self.Form.Head.data
                        date = self.toSpecial(self.Form.Date.data)  # 将.分隔转化为#分隔
                        content = self.Form.Postcontent.data
                        print(self.Form.data)
                        print(xh, head, date, content)
                        self.Cursor.execute("select identity from admin_ where xh = :s", [self.Form.Xh.data])
                        i = self.Cursor.fetchone()
                        if i:
                            if i[0] == 0: # 系统公告
                                filename = xh  + date + ".txt" # 每个用户的文章以学号标题日期作为文件名
                                self.Cursor.execute("select * from admin_post where xh = :s and postdate = :s", [xh, date]) # 用户在该天写了公告
                                if self.Cursor.fetchone(): # 查到就只需要更改文章内容即可
                                    with open(current_app.config["DOWNLOADPATHP"] + "/" + filename, "w", encoding="utf-8") as file:
                                        file.write(content)
                                    self.Cursor.execute("update admin_post set head = :s where xh = :s and postdate = :s", [head, xh, date])
                                    self.DB.commit()
                                else: # 否则没查到就得添加一篇文章
                                    with open(current_app.config["DOWNLOADPATHP"] + "/" + filename, "w", encoding="utf-8") as file:
                                        file.write(content)
                                    self.Cursor.execute("insert into admin_post values (:s, :s, :s, :s)", [xh, head, date, filename])
                                    self.DB.commit()
                                return redirect("/admin/system")
                            else:
                                return render_template("admin_setting.html", identity="admin", name=session["user"], proxy="",
                                                   posts=posts,
                                                   applies=xh_identity_xm, postform=self.Form,
                                                   postmsg="您只可查看教师的课程公告")
                        else:
                            return render_template("admin_setting.html", identity="admin", name=session["user"], proxy="",
                                                   posts=posts,
                                                   applies=xh_identity_xm, postform=self.Form,
                                                   postmsg="输入表单有误，学号不存在")
                    else:
                        return render_template("admin_setting.html", identity="admin", name=session["user"], proxy="", posts=posts,
                                           applies=xh_identity_xm, postform=self.Form, postmsg="请按表单要求格式输出")
        else:
            return redirect("/errormsg/1")

    def __del__(self):
        self.Cursor.close()
        self.DB.close()


class AdminUsers(views.View): # 分为一个get和一个ajax post
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()

    def noquery_check_identity(self):
        self.Cursor.execute("select xh from admin_ where identity = 0")
        if (session["user"],) in self.Cursor.fetchall():
            return 1
        else:
            return "/errormsg/1"

    def dispatch_request(self):
        if session.get("user"):
            check_result = self.noquery_check_identity()
            if isinstance(check_result, str):
                return redirect(check_result)
            else:
                if request.method == "GET":
                    self.Cursor.execute("select xh, pwd from admin_ where identity = 1")
                    stu_xh_pwd = self.Cursor.fetchall()
                    self.Cursor.execute("select xh, pwd from admin_ where identity = 2")
                    tea_xh_pwd = self.Cursor.fetchall()
                    studentmanage = list()
                    teachermanage = list()
                    for i in range(len(stu_xh_pwd)):
                        xh = stu_xh_pwd[i][0]
                        pwd = stu_xh_pwd[i][1]
                        self.Cursor.execute("select permission from modify_infor_permission where xh = :s", [xh])
                        permission = self.Cursor.fetchone()[0]
                        studentmanage.append(UserManage((xh, pwd, permission)))
                    for j in range(len(tea_xh_pwd)):
                        xh = tea_xh_pwd[j][0]
                        pwd = tea_xh_pwd[j][1]
                        self.Cursor.execute("select permission from modify_infor_permission where xh = :s", [xh])
                        permission = self.Cursor.fetchone()[0]
                        teachermanage.append(UserManage((xh, pwd, permission)))
                    return render_template("users.html", identity="admin", proxy="", name=session["user"], students=studentmanage, teachers=teachermanage)
                else:
                    xhs = request.form.getlist("xhs[]")
                    pwds = request.form.getlist("pwds[]")
                    permissions = request.form.getlist("permissions[]")
                    types = request.form.getlist("types[]")
                    for i in pwds:
                        if len(i) < 4 or len(i) > 18:
                            return "添加失败！密码长度有误"
                    # try:
                    for i in range(len(xhs)):
                        default_content = (xhs[i], "未填写", "未填写", "未填写", "未填写（中国大陆居民身份证）", "未填写（年.月.日）",
                                           "未填写", "未填写", "未填写（班号）", "未填写", "未填写（邮箱格式）", "未填写（学生类型）", "未填写（入学时间）",
                                           0, "未填写", "未填写", "default.jpg")
                        default_content1 = [xhs[i], "未填写", "未填写", "未填写", "未填写（可选）", "未填写", "未填写（中国大陆居民身份证）",
                                            "未填写", "未填写", "未填写", "未填写", "未填写（邮箱格式）", "未填写（入职时间）", "未填写", "default.jpg"]

                    try:
                        self.Cursor.execute("insert into admin_ values (:s, :s, :s)", [xhs[i], pwds[i], 1 if types[i]=="s" else 2])
                        self.Cursor.execute("insert into modify_infor_permission values (:s, :s, :s, 0)", [xhs[i], session["user"], permissions[i]])
                        if types[i] == "s":
                            self.Cursor.execute("insert into student_infor values (:s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s)", default_content)
                        else:
                            self.Cursor.execute("insert into employee_infor values (:s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s, :s)", default_content1)
                        self.DB.commit()
                    except:
                        self.DB.rollback()
                        return "添加失败！账号重复"
                    else:
                        return "添加成功！"
        else:
            return "添加失败！权限不足"

    def __del__(self):
        self.Cursor.close()
        self.DB.close()


class AdminInfor(views.View):
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()
        self.get = AdminIndex()
        self.Form = EmployeeinforClass()
        self.all_fields = ['xh', 'xm', 'mz', 'sex', 'marry', 'society', 'id', 'major',
                           'dept', 'job', 'phone', 'mail', 'comedate', 'address']

    def copy_form(self):
        self.Cursor.execute("select * from employee_infor where xh = :s", [request.args.get("xh")])
        infor_tuple = self.Cursor.fetchone()
        self.Form.Xh.data = infor_tuple[0]
        self.Form.Xm.data = infor_tuple[1]
        self.Form.Mz.data = infor_tuple[2]
        self.Form.Sex.data = infor_tuple[3]
        self.Form.Marry.data = infor_tuple[4]
        self.Form.Society.data = infor_tuple[5]
        self.Form.Id.data = infor_tuple[6]
        self.Form.Major.data = infor_tuple[7]
        self.Form.Dept.data = infor_tuple[8]
        self.Form.Job.data = infor_tuple[9]
        self.Form.Phone.data = infor_tuple[10]
        self.Form.Mail.data = infor_tuple[11]
        self.Form.Comedate.data = infor_tuple[12]
        self.Form.Address.data = infor_tuple[13]
        self.avatarname = infor_tuple[14]

    def get_postsql(self, type):
        if self.Form.Avatar.data.filename:  # 上传头像文件
            RE = ".*(\..*)$"
            end = re.findall(RE, self.Form.Avatar.data.filename)[0]
            randomstring = ''.join(
                random.sample('zyxwvutsrqponmlkjihgfedcba%ZAQWESDFYRUIOOMJ', 10)
            )  # 在上述字符中随机10个作为文件名以防浏览器缓存的直接调取
            filename = randomstring + end
            self.Cursor.execute("select image from employee_infor where xh = :s", [request.args.get("xh")])  # 查询原文件名
            img = self.Cursor.fetchone()[0]
            if type == "admin":
                path = "DOWNLOADPATHA"
            else:
                path = "DOWNLOADPATHT"
            if img != "default.jpg":
                os.remove(os.path.join(current_app.config["DOWNLOADPATHA"], img))  # 删除原文件
                self.Form.Avatar.data.save(os.path.join(current_app.config[path], filename))  # 存取新文件
            else:
                self.Form.Avatar.data.save(os.path.join(current_app.config[path], filename))
            # 带有文件修改的sql
            sql = "update employee_infor set xm='%s',mz='%s',sex='%s',marry='%s',society='%s',id='%s',major='%s',dept='%s',phonenumber='%s',mail='%s',comedate='%s'," \
                  "address='%s',image='%s' where xh = '%s'" % (
                  self.Form.Xm.data, self.Form.Mz.data, self.Form.Sex.data, self.Form.Marry.data,
                  self.Form.Society.data, self.Form.Id.data, self.Form.Major.data, self.Form.Dept.data,
                  self.Form.Phone.data, self.Form.Mail.data, self.Form.Comedate.data, self.Form.Address.data,
                  filename, request.args.get("xh"))
        else:
            sql = "update employee_infor set xm='%s',mz='%s',sex='%s',marry='%s',society='%s',id='%s',major='%s',dept='%s',phonenumber='%s',mail='%s',comedate='%s'," \
                  "address='%s' where xh = '%s'" % (
                  self.Form.Xm.data, self.Form.Mz.data, self.Form.Sex.data, self.Form.Marry.data,
                  self.Form.Society.data, self.Form.Id.data, self.Form.Major.data, self.Form.Dept.data,
                  self.Form.Phone.data, self.Form.Mail.data, self.Form.Comedate.data, self.Form.Address.data,
                  request.args.get("xh"))
        return sql

    def dispatch_request(self):
        if session.get("user"):
            check_result = self.get.check_identity()
            if isinstance(check_result, str):
                return redirect(check_result)
            else:
                if request.method == "GET":
                    self.copy_form()
                    return render_template("infor.html", form=self.Form, identity="admin", name=session["user"], realname=self.Form.Xm.data, toNone=False,
                                            proxy="", modify=1, first="", all_fields=self.all_fields, avatar=self.avatarname)
                else:
                    if self.Form.validate_on_submit() and self.Form.Xh.data == "":
                        self.Cursor.execute("select xh, xm from employee_infor where xh = :s",
                                            [request.args.get("xh")])
                        xh_xm = self.Cursor.fetchone()
                        try:
                            sql = self.get_postsql("admin")
                            self.Cursor.execute(sql)
                            self.DB.commit()
                        except:
                            self.Cursor.execute("select image from employee_infor where xh = :s",
                                                [request.args.get("xh")])
                            self.avatarname = self.Cursor.fetchone()[0]
                            self.DB.rollback()
                            return render_template("infor.html", form=self.Form, identity="admin", name=session["user"], realname=self.Form.Xm.data, toNone=False,
                                                   proxy="", modify=1, first="", all_fields=self.all_fields, avatar=self.avatarname, errormsg="修改失败，请稍后重试")
                        else:
                            return redirect("/admin/information?xh=" + session["user"])
                    else: # 验证器报错或者用户修改了学号
                        self.Cursor.execute("select image from employee_infor where xh = :s",
                                            [request.args.get("xh")])
                        self.avatarname = self.Cursor.fetchone()[0] # 用户修改内容但未修改图片时的情况，需要将图片返还
                        for i in list(self.Form.errors.keys()):
                            self.Form[i].data = ""
                        return render_template("infor.html", form=self.Form, identity="admin", name=session["user"], realname=self.Form.Xm.data, toNone=False,
                                               proxy="", modify=1, first="", all_fields=self.all_fields, avatar=self.avatarname, errormsg="学号不可更改且请按表单要求输入")
        else:
            return redirect("/errormsg/1")

    def __del__(self):
        self.Cursor.close()
        self.DB.close()


@Adminbp.route("/admin/<type>/user/<xh>", methods=["POST"])
def ManageUser(type, xh):
    if session.get('user'):
        check_result = AdminUsers().noquery_check_identity()
        if isinstance(check_result, str):
            return redirect(check_result)
        else:
            if request.method == "POST":
                if xh:
                    DB = current_app.config["DATABASE"].connection()
                    cursor = DB.cursor()
                    if type == "delete":
                        try:
                            cursor.execute("delete from admin_ where xh = :s", [xh])
                            DB.commit()
                        except:
                            DB.rollback()
                            return "输入的学号不正确"
                        else:
                            return "删除成功"
                    elif type == "modify":
                        pwd = request.form.get("pwd")
                        checked = request.form.get("checked")
                        try:
                            cursor.execute("update admin_ set pwd = :s where xh = :s", [pwd, xh])
                            cursor.execute("update modify_infor_permission set permission = :s where xh = :s", [checked, xh])
                            DB.commit()
                        except:
                            DB.rollback()
                            return "输入的学号不正确"
                        else:
                            return "修改成功"
                    else:
                        return redirect("/errormsg/3")
                else:
                    return redirect("/errormsg/3")
            else:
                return redirect("/errormsg/4")

    else:
        return "权限不足"

@Adminbp.route("/managerequest/<type>/<xh>", methods=["GET"])
def Manageinforrequest(type, xh):
    if session.get('user'):
        check_result = AdminUsers().noquery_check_identity()
        if isinstance(check_result, str):
            return redirect(check_result)
        else:
            if request.method == "GET":
                print("jajaaj")
                DB = current_app.config["DATABASE"].connection()
                cursor = DB.cursor()
                if type == "agree":
                    try:
                        cursor.execute("update modify_infor_permission set permission = 1, posted = 0 where xh = :s", [xh])
                        DB.commit()
                    except:
                        DB.rollback()
                        return "允许申请操作失败"
                    else:
                        return "允许申请操作成功"
                else:
                    try:
                        cursor.execute("update modify_infor_permission set posted = 0 where xh = :s", [xh])
                        DB.commit()
                    except:
                        DB.rollback()
                        return "删除申请操作失败"
                    else:
                        return "删除申请操作成功"
            else:
                return redirect("/errormsg/4")

    else:
        return "权限不足"

@Adminbp.route("/admin/<type>/post", methods=["POST"])
def ManagePost(type):
    if session.get("user"):
        check_result = AdminUsers().noquery_check_identity()
        if isinstance(check_result, str):
            return redirect(check_result)
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

            if type == "delete":
                try:
                    cursor.execute("select txtpath from admin_post where xh = :s and postdate = :s", [xh, date])
                    os.remove(current_app.config["DOWNLOADPATHP"] + '/' + cursor.fetchone()[0])
                    cursor.execute("delete from admin_post where xh = :s and postdate = :s", [xh, date])
                    DB.commit()
                except:
                    DB.rollback()
                    return "删除失败"
                else:
                    return "删除成功"
            elif type == "get":
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

@Adminbp.route("/all/course", methods=["POST", "GET"])
def AllCourse():
    if session.get("user"):
        check_result = AdminUsers().noquery_check_identity()
        if isinstance(check_result, str):
            return redirect(check_result)
        else:
            DB = current_app.config["DATABASE"].connection()
            cursor = DB.cursor()
            if request.method == "GET":
                xm = cursor.execute("select xm from employee_infor where xh = :s", [session["user"]]).fetchone()[0]
                courses_infor = cursor.execute("select kh, kname, kcredit, kamount, testtype, kteacher from course order by kteacher").fetchall()
                return render_template("course.html", proxy="", identity="admin", name=session["user"], realname=xm, courses=courses_infor)
            else:
                try:
                    cursor.execute("delete from sc where kh = :s", [request.form.get("kh")])
                    cursor.execute("delete from course where kh = :s", [request.form.get("kh")])
                    DB.commit()
                except:
                    DB.rollback()
                    return "修改失败"
                else:
                   return "修改成功"
    else:
        return redirect("/errormsg/1")