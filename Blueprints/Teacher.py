from flask import Blueprint, views, current_app, session, request, redirect,render_template, jsonify
from .Manager import toNormal
from Formclasses.student_classes import DiaryandPost
from Formclasses.admin_classes import AinforClass, EmployeeinforClass
from .Admin import AdminInfor
import datetime
import re

Teacherbp= Blueprint("teacher", __name__)

class TeacherIndex(views.View):
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()

    def check_identity(self):
        if request.args.get("xh"):
            xh = request.args.get("xh")
            self.Cursor.execute("select xh from admin_ where identity = 2")
            teacher_xhs = self.Cursor.fetchall()
            if (xh,) in teacher_xhs:
                self.Cursor.execute(
                    "select identity from admin_ where xh = '%s'" % session["user"]
                )  # 用当前登陆的用户查询权限
                if xh == session["user"]:  # 如果当前登陆的用户与查询字符串中一致
                    return 1
                elif self.Cursor.fetchone()[0] == 0:  # 否则若登陆用户权限为管理员
                    return 0
                else:  # 既不是管理员也不是当前登陆的用户，无权查看
                    return "/errormsg/1"
            else:
                return "/errormsg/1"
        else:
            return "/errormsg/2"

    def dispatch_request(self):
        if session.get("user"):
            check_result = self.check_identity()
            if isinstance(check_result, str):
                return redirect(check_result)
            else:
                if request.method == "GET":
                    self.Cursor.execute("select head, postdate, xh from admin_post order by postdate desc")
                    result = self.Cursor.fetchall()
                    admin_posts = list()
                    for i in result:
                        admin_posts.append(
                            {"head": i[0], "time": toNormal(i[1], "second"), "xh": i[2]}
                        )  # 获取系统公告的标题和发布时间及发布人
                    teacher_posts = list()
                    self.Cursor.execute("select head, postdate, to_char(kh, '00000') from teacher_post where xh = :s order by postdate desc",
                                        [request.args.get("xh")])
                    result = self.Cursor.fetchall()
                    for i in result:
                        teacher_posts.append(
                            {"head": i[0], "time": toNormal(i[1], "second"), "kh": i[2]}
                        ) # 获取当前查询教师所发布的课程通告
                    if check_result == 1:
                        self.Cursor.execute(
                            "select xh, xm, sex, dept, major, job, comedate, image from employee_infor where xh = :s",
                            [session["user"]])
                        infor = self.Cursor.fetchone()
                        sinfor = AinforClass(infor)  # 造studentinformation对象，包含教师用户部分基本信息
                        if sinfor.getimage() == "default.jpg":
                            first = 1
                        else:
                            first = 0
                        today = datetime.date.today()  # 获取今天日期
                        date = session["user"] + str(today.year) + "#" + str(today.month) + "#" + str(today.day)
                        self.Cursor.execute("select txtpath from users_diary where xh = :s", [session["user"]])
                        if (date + ".txt",) in self.Cursor.fetchall():  # 返回本人当天日记内容前先找找有没有这个文件
                            with open(current_app.config["DOWNLOADPATHT"] + "\\" + toNormal(date, "first") + ".txt", "r", encoding="utf-8") as file:
                                content = file.read()
                        else:  # 找不到就返回空给content
                            content = ""
                        dpform = DiaryandPost((content, admin_posts, teacher_posts))  # 该对象包括公告信息
                        return render_template("index.html", identity='teacher', dpform=dpform, proxy="", basic_infor=sinfor, name=infor[0], first=first)
                    else:
                        content = "此为该用户隐私，您无权访问"
                        dpform = DiaryandPost((content, admin_posts, teacher_posts))  # 该对象包括公告信息
                        self.Cursor.execute(
                            "select xh, xm, sex, dept, major, job, comedate, image from employee_infor where xh = :s",
                            [request.args.get("xh")])  # 查部分基本信息
                        infor = self.Cursor.fetchone()
                        sinfor = AinforClass(infor)  # 造studentinformation对象，包含用户部分基本信息
                        return render_template("index.html", identity='teacher', dpform=dpform, proxy=session["user"],
                                               first=1 if sinfor.getimage() == "default.jpg" else 0, basic_infor=sinfor, name=infor[0])
                else:
                    return redirect("/errormsg/4")
        else: # 没有session就回去登陆
            return redirect("/")

    def __del__(self):
        self.Cursor.close()
        self.DB.close()

class Teacherinfor(views.View):
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()
        self.get = TeacherIndex()
        self.Form = EmployeeinforClass()
        self.getpost = AdminInfor()
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

    def check_permission(self, user):
        self.Cursor.execute("select permission from MODIFY_INFOR_PERMISSION where xh = :s", [user])
        return self.Cursor.fetchone()[0]

    def toNone_and_setNull(self):
        self.Cursor.execute("select image from employee_infor where xh = :s",
                            [request.args.get("xh")])
        self.avatarname = self.Cursor.fetchone()[0]
        toNone = False  # 代表表单int字段出错时是否返回为空，下面遍历错误键时出现Years该字段置True
        for i in list(self.Form.errors.keys()):
            if i == "Years":
                toNone = True
            self.Form[i].data = ""
        return toNone

    def dispatch_request(self):
        if session.get("user"):
            check_result = self.get.check_identity()
            if isinstance(check_result, str):
                return redirect(check_result)
            else:
                if request.method == "GET":
                    permission = self.check_permission(request.args.get("xh"))
                    self.copy_form()
                    if self.avatarname == "default.jpg":  # 是否为刚添加的用户
                        first_time = 1
                    else:
                        first_time = 0
                    if check_result == 0:  # 管理员进入
                        self.Cursor.execute("select xm from employee_infor where xh = :s", [session["user"]])
                        proxy_name = self.Cursor.fetchone()[0]
                        return render_template("infor.html", proxy=proxy_name, modify=1, name=self.Form.Xh.data,
                                               realname=self.Form.Xm.data,
                                               form=self.Form, all_fields=self.all_fields, avatar=self.avatarname,
                                               first=first_time, identity="teacher")
                    else:  # 本人进入
                        return render_template("infor.html", proxy="", modify=permission, name=self.Form.Xh.data,
                                               realname=self.Form.Xm.data,
                                               form=self.Form, all_fields=self.all_fields, avatar=self.avatarname,
                                               first=first_time, identity="teacher")
                else:
                    permission = self.check_permission(request.args.get("xh"))
                    if check_result == 0: # 管理员
                        self.Cursor.execute("select xm from employee_infor where xh = :s", [session["user"]])
                        proxy_name = self.Cursor.fetchone()[0]
                        self.Cursor.execute("select xh, xm from employee_infor where xh = :s",
                                            [request.args.get("xh")])
                        xh_xm = self.Cursor.fetchone()
                        if self.Form.validate_on_submit() and self.Form.Xh.data == "":
                            sql = self.getpost.get_postsql("teacher") # 调用getsql方法处理是否进行文件上传，得到对应的sql语句
                            try:
                                self.Cursor.execute(sql)
                                self.DB.commit()
                            except:
                                self.Cursor.execute("select image from employee_infor where xh = :s", [request.args.get("xh")])
                                self.avatarname = self.Cursor.fetchone()[0]
                                self.DB.rollback()
                                return render_template("infor.html", proxy=proxy_name, modify=1,
                                                       name=xh_xm[0], realname=xh_xm[1],
                                                       form=self.Form, all_fields=self.all_fields,
                                                       errormsg="修改失败，请仔细查看学号冲突", avatar=self.avatarname, identity="teacher")
                            else: # sql和收回权限没有出现错误，就get当前url
                                return redirect("/teacher/information?xh=%s" % (request.args.get("xh")))
                    else: # 本人
                        if permission == 0: # 无修改权限
                            return render_template("infor.html", proxy="", modify=permission, name=self.Form.Xh.data, realname=self.Form.Xm.data,
                                                   form=self.Form, all_fields=self.all_fields, errormsg="您无权限更改信息", avatar=self.avatarname, identity="teacher")
                        else:
                            self.Cursor.execute("select xh, xm from employee_infor where xh = :s",
                                                [request.args.get("xh")])
                            xh_xm = self.Cursor.fetchone()
                            if self.Form.validate_on_submit() and self.Form.Xh.data == "": # 不可更改学号，因此能够修改信息的条件就是学号不为空并且表单认证完成
                                print("benren")
                                try:
                                    sql = self.getpost.get_postsql("teacher")
                                    # 用户获取权限后仅供成功修改一次
                                    self.Cursor.execute("update modify_infor_permission set permission = 0 where xh = :s",
                                                        [request.args.get("xh")])
                                    self.Cursor.execute(sql)
                                    self.DB.commit()
                                except:
                                    self.Cursor.execute("select image from employee_infor where xh = :s", [request.args.get("xh")])
                                    self.avatarname = self.Cursor.fetchone()[0]
                                    if self.avatarname == "default.jpg":
                                        first_time = 1
                                    else:
                                        first_time = 0
                                    self.DB.rollback()
                                    return render_template("infor.html", proxy="", modify=permission,
                                                           name=self.Form.Xh.data, realname=self.Form.Xm.data,
                                                           form=self.Form, all_fields=self.all_fields, first=first_time,
                                                           errormsg="修改失败，请稍后重试", avatar=self.avatarname, identity="teacher")
                                else: # sql和收回权限没有出现错误，就get当前url
                                    return redirect("/teacher/information?xh=%s" % (request.args.get("xh"),))

                            else: # 验证器出现问题
                                toNone = self.toNone_and_setNull()
                                if self.avatarname == "default.jpg":
                                    first_time = 1
                                else:
                                    first_time = 0
                                return render_template("infor.html", proxy="", modify=permission, name=xh_xm[0], realname=xh_xm[1], toNone=toNone,
                                                       form=self.Form, all_fields=self.all_fields, errormsg="学号不可更改，请按表单要求输入",
                                                       avatar=self.avatarname, first=first_time, identity="teacher")
        else:
            return redirect("/errormsg/1")

    def __del__(self):
        self.Cursor.close()
        self.DB.close()

class Teachercourse(views.View):
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()
        self.get = TeacherIndex()

    def dispatch_request(self):
        if session.get("user"):
            check_result = self.get.check_identity()
            if isinstance(check_result, str):
                return redirect(check_result)
            else:
                if request.method == "GET":
                    realname = self.Cursor.execute("select xm from employee_infor where xh = :s", [request.args.get("xh")]).fetchone()[0]
                    courses = self.Cursor.execute("select to_char(kh, '000000'), kname, khours, knature, kcredit, testtype, kamount from course where kteacher = :s", [request.args.get("xh")])
                    if check_result == 0:
                        return render_template("course.html", proxy=session["user"], identity="teacher", realname=realname, name=request.args.get("xh"), courses=courses)
                    else:
                        return render_template("course.html", proxy='', identity="teacher", realname=realname, name=request.args.get("xh"), courses=courses)
                else:
                    kh = int(request.form.get("kh").lstrip('0'))
                    try:
                        kh_students = self.Cursor.execute("select sc.xh, xm, sex, major, dept, normalgrade, examgrade, finalgrade from student_infor, sc where sc.xh = student_infor.xh and kh = :s", [kh]).fetchall()
                        courses_infor = list(self.Cursor.execute("select examdate, normalqz, examqz from course where kteacher = :s and kh = :s", [request.args.get("xh"), kh]).fetchone())
                        if courses_infor[0]:
                            date = courses_infor[0].split("#")[0] + "." + courses_infor[0].split("#")[1] + "." + courses_infor[0].split("#")[2]
                            courses_infor[0] = date
                        xhs =  list()
                        xms = list()
                        sexs = list()
                        majors = list()
                        depts = list()
                        normalgrades = list()
                        examgrades = list()
                        finalgrades = list()
                        for i in kh_students:
                            xhs.append(i[0])
                            xms.append(i[1])
                            sexs.append(i[2])
                            majors.append(i[3])
                            depts.append(i[4])
                            normalgrades.append(i[5] if i[5] else "")
                            examgrades.append(i[6] if i[6] else "")
                            finalgrades.append(i[7] if i[7] else "")
                        return jsonify(
                            {"msg": "success", "xh": xhs, "xm": xms, "sex": sexs, "major": majors,
                             "dept": depts, "normalgrade":normalgrades, "examgrade":examgrades,
                             "finalgrade":finalgrades, "courseinfor": courses_infor}
                        )
                    except:
                        return jsonify({"msg": "failed"})
        else:
            return redirect("/errormsg/1")

@Teacherbp.route("/teacher/modify/grade", methods=["POST", "GET"])
def ModifyGrade():
    get = TeacherIndex()
    if session.get("user"):
        check_result = get.check_identity()
        if isinstance(check_result, str):
            return redirect(check_result)
        else:
            if request.method == "POST":
                if check_result == 0:
                    return "抱歉，您无权修改"
                else:
                    DB = current_app.config["DATABASE"].connection()
                    Cursor = DB.cursor()
                    try:
                        examdate = request.form.get("examdate")
                        if examdate:
                            RE = "^([0-9][0-9][0-9][0-9])\.(1[0-2]|0[1-9]|[1-9])\.(3[0-1]|2[0-9]|1[0-9]|0[1-9]|[1-9])$"
                            result = re.findall(RE, examdate)
                            if len(result) != 1:
                                return "修改失败，日期格式有误"
                            date = ""
                            date += result[0][0]
                            date += "#"
                            date += "0" + result[0][1] if len(result[0][1])==1 else result[0][1]
                            date += "#"
                            date += "0" + result[0][2] if len(result[0][2])==1 else result[0][2]
                        else:
                            date = ""
                        try:
                            normalqz = float(request.form.get("normalqz"))
                            examqz = 1 - normalqz
                        except:
                            normalqz = ""
                            examqz = ""
                        if examqz < 0 or normalqz < 0 or examqz > 1 or normalqz > 1:
                            normalqz = ""
                            examqz = ""
                        try:
                            normalgrade = float(request.form.get("normalgrade"))
                            examgrade = float(request.form.get("examgrade"))
                        except:
                            return "修改失败，成绩格式有误"
                        if normalqz == "":
                            finalgrade = ""
                        else:
                            finalgrade = normalgrade * normalqz + examgrade * examqz
                        Cursor.execute("update course set EXAMDATE = :s, EXAMQZ = :s, NORMALQZ = :s where kteacher = :s and kh = :s", [date, examqz, normalqz, request.args.get("xh"), request.form.get("kh")])
                        Cursor.execute("update sc set normalgrade = :s, examgrade = :s, finalgrade = :s where kh = :s and xh = :s", [normalgrade, examgrade, finalgrade, request.form.get("kh"), request.form.get("xh")])
                        DB.commit()
                    except:
                        DB.rollback()
                        return "修改失败，成绩大小有误"
                    else:
                        return "修改成功"
            else:
                return redirect("/errormsg/4")

@Teacherbp.route("/teacher/course/add", methods=["POST", "GET"])
def CourseAdd():
    get = TeacherIndex()
    if session.get("user"):
        check_result = get.check_identity()
        if isinstance(check_result, str):
            return redirect(check_result)
        else:
            if request.method == "POST":
                if check_result == 0:
                    return "抱歉，您无权修改"
                else:
                    try:
                        DB = current_app.config["DATABASE"].connection()
                        Cursor = DB.cursor()
                        kname = request.form.getlist("kname[]")
                        khours = request.form.getlist("khours[]")
                        knatures = request.form.getlist("knatures[]")
                        ktestypes = request.form.getlist("ktestypes[]")
                        kamounts = request.form.getlist("kamounts[]")
                        knormalqzs = request.form.getlist("knormalqzs[]")
                        kexamqzs = request.form.getlist("kexamqzs[]")
                        if "" in kname or "" in khours or "" in knatures or "" in ktestypes or "" in kamounts:
                            return "required提示字段不可为空"
                        for i in range(len(kname)):
                            Cursor.execute("insert into course(kname, kteacher, KHOURS, knature, kcredit, KAMOUNT, TESTTYPE, normalqz, examqz)"
                                           " values (:s, :s, :s, :s, :s, :s, :s, :s, :s)", [kname[i], request.args.get("xh"),int(khours[i]), knatures[i], float(float(khours[i])/16), kamounts[i], ktestypes[i], float(knormalqzs[i]), 1-float(knormalqzs[i])])
                        DB.commit()
                    except:
                        return "添加失败，表单格式有误"
                    else:
                        return "添加成功"
            else:
                return redirect("/errormsg/4")