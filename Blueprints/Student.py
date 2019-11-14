from flask import Blueprint, views, session, current_app, redirect, request, render_template, jsonify
from Formclasses.student_classes import SinforClass, DiaryandPost, StudentinforClass
import datetime
import re
import os
from .Manager import toNormal
import random
from .Admin import AdminIndex
from .Teacher import TeacherIndex

Studentbp = Blueprint("student", __name__)
@Studentbp.route("/addrequest/<type>", methods=[ "GET"])
def Addinforrequest(type): # 两种申请
    if session.get("user"):
        db = current_app.config["DATABASE"].connection()
        cursor = db.cursor()
        if type == "course":
            pass
        else:
            cursor.execute("select permission from modify_infor_permission where xh = :s", [request.form.get("xh")])
            permission = cursor.fetchone()[0]
            if permission == 0:
                try:
                    cursor.execute("update modify_infor_permission set posted = 1 where xh = :s", [request.form.get("xh")])
                    db.commit()
                except:
                    db.rollback()
                    return "sqlerror"
                else:
                    return "success"
            else:
                return "have"
    else:
        return "sqlerror"


#学生权限：设计为所有学生和教师之间权限共等，互相不可访问
class StudentIndex(views.View): # 主页，只有get请求
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()

    def dispatch_request(self):
        if session.get("user"): # 首先确定登陆session
            if request.method == "GET": # 仅get请求
                check_result = self.check_identity()
                if isinstance(check_result, str):
                    return redirect(check_result)
                else:
                    # 以下部分是查公告表的内容并返回，包括系统公告和课程公告
                    self.Cursor.execute("select head, postdate, xh from admin_post order by postdate desc")
                    result = self.Cursor.fetchall()
                    admin_posts = list()
                    for i in result:
                        admin_posts.append(
                            {"head": i[0], "time": toNormal(i[1], "second"), "xh": i[2]})  # 获取系统公告的标题和发布时间及发布人
                    self.Cursor.execute("select head, postdate, to_char(kh) from teacher_post where kh in (select kh from sc where xh = :s) order by postdate desc",
                                        [request.args.get("xh")])
                    result = self.Cursor.fetchall()
                    teacher_posts = list()
                    for i in result:
                        teacher_posts.append(
                            {"head": i[0], "time": toNormal(i[1], "second"), "kh": i[2]}
                        )  # 获取课程公告的标题和发布时间及发布课程
                    if check_result == 0:  # 管理员进入该用户主页，除了日记无法访问其余与登录者完全相同
                        content="此为该用户隐私，您无权访问"
                        dpform = DiaryandPost((content, admin_posts, teacher_posts))  # 该对象包括公告信息
                        self.Cursor.execute(
                            "select xh, xm, sex, dept, major, class, comedate, image from student_infor where xh = :s",
                            [request.args.get("xh")])  # 查部分基本信息
                        infor = self.Cursor.fetchone()
                        sinfor = SinforClass(infor)  # 造studentinformation对象，包含用户部分基本信息
                        if infor[7] == "default.jpg": # 第一次登陆时照片为default
                            first_time = 1
                        else:
                            first_time = 0
                        return render_template("index.html", basic_infor=sinfor, proxy=session["user"], name=request.args.get("xh"), identity="student", dpform=dpform, first=first_time)

                    elif check_result == 1:  # 用户自己进入主页
                        self.Cursor.execute(
                            "select xh, xm, sex, dept, major, class, comedate, image from student_infor where xh = :s",
                            [session["user"]])  # 查部分基本信息
                        infor = self.Cursor.fetchone()
                        sinfor = SinforClass(infor)  # 造studentinformation对象，包含用户部分基本信息
                        if infor[7] == "default.jpg": # 第一次登陆时照片为default.jpg
                            first_time = 1
                        else:
                            first_time = 0
                        today = datetime.date.today() # 获取今天日期
                        user_date = session["user"] + toNormal(str(today.year) + "#" + str(today.month) + "#" + str(today.day), "first")
                        txtpaths = self.Cursor.execute("select txtpath from users_diary where xh = :s", [session["user"]]).fetchall()
                        if (user_date + ".txt",) in txtpaths: # 返回本人当天日记内容前先找找有没有这个文件
                            with open(current_app.config["DOWNLOADPATHS"] + "\\" + toNormal(user_date, "first") + ".txt", "r", encoding="utf-8") as file:
                                content = file.read()
                        else: # 找不到就返回空给content
                            content = ""
                        print(content)
                        dpform = DiaryandPost((content, admin_posts, teacher_posts))  # 该对象包括公告信息
                        return render_template("index.html", proxy="", name=infor[0], basic_infor=sinfor, dpform=dpform, identity="student", first=first_time)

                    else: # 外人
                        return redirect("/errormsg/1")
            else:
                return redirect("/errormsg/4")
        else: # 没有session先回去
            return redirect("/")

    def check_identity(self):
        '''
        检查逻辑：
        先判断query是否存在，再判query是否为库内所有学生，再判当前登陆者是否为本人或管理员
        '''
        if request.args.get("xh"):
            xh = request.args.get("xh")
            self.Cursor.execute("select xh from admin_ where identity = 1")
            student_xhs = self.Cursor.fetchall()
            if (xh,) in student_xhs:
                self.Cursor.execute(
                    "select identity from admin_ where xh = '%s'" % session["user"]
                )  # 用当前登陆的用户查询权限
                if xh == session["user"]: # 为本人
                    return 1
                elif self.Cursor.fetchone()[0] == 0: # 不为本人，但为管理员
                    return 0
                else:
                    return "/errormsg/1"
            else:
                return "/errormsg/1"
        else:
            return "/errormsg/2"

    def __del__(self):
        self.Cursor.close()
        self.DB.close()

class DiaryPostView(views.View): # 管理日记的提交，有两个ajax请求
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()
        self.getS = StudentIndex()
        self.getA = AdminIndex()
        self.getT = TeacherIndex()

    def dispatch_request(self):
        if request.method == "GET": # 用户通过点击日历get方法查看日记
            if session.get("user"):
                result = ""
                if request.args.get("type") == "admin":
                    result = self.getA.check_identity() # 管理员的日记
                elif request.args.get("type") == "student":
                    result = self.getS.check_identity() # 学生的日记
                else:
                    result = self.getT.check_identity() # 教师的日记
                if isinstance(result, str):# 返回为str错误消息路由则跳转
                    return redirect(result)
                else:
                    if result == 1: # 权限下来为1，即登陆者本人方可查询日记，管理员方面则只有返回1和重定向路径的情况
                        date = request.args.get("date")
                        xh = request.args.get("xh")
                        self.Cursor.execute("select txtpath from users_diary where xh = :s", [xh]) # 查该用户这天的文件是否存在
                        txtuple = self.Cursor.fetchall()
                        if (xh + date + ".txt",) in txtuple: # 存在则输出
                            if request.args.get("type") == "student":
                                path = "DOWNLOADPATHS"
                            elif request.args.get("type") == "teacher":
                                path = "DOWNLOADPATHT"
                            else:
                                path = "DOWNLOADPATHA"
                            with open(current_app.config[path] + "\\" + xh + date + ".txt", "r", encoding="utf-8") as file:
                                body = file.read()
                        else: # 不存在返回空
                            body = ""
                    else: # 权限下来为0，即管理员登陆
                        body = "此为该用户隐私，您无权访问"
                    return body
            else:
                return redirect("/errormsg/1")
        else: # post请求
            if session.get("user"):
                xh = request.form.get("xh") # 因为没有url查询字符串所以不能用index中的checkidentity方法，直接将表单内容与登陆session判断即可
                if session["user"] == xh:
                    date = request.form.get("date")
                    body = request.form.get("body")
                    # 每次有body内容就将文件重写一遍，而open中w方式也会没有文件时直接创建，因此无需判断文件是否存在
                    if request.form.get("type") == "student":
                        path = "DOWNLOADPATHS"
                    elif request.form.get("type") == "teacher":
                        path = "DOWNLOADPATHT"
                    else:
                        path = "DOWNLOADPATHA"
                    print(current_app.config[path] + "\\" +  xh + date + ".txt")
                    with open(current_app.config[path] + "\\" +  xh + date + ".txt", "w", encoding="utf-8") as file:
                        file.write(body)
                    # 因为数据库存的只是txt文件的名称加后缀，所以只要数据库有这个文件名就不需要再insert或update了
                    self.Cursor.execute("select xh, txtpath from users_diary")
                    xh_txtpathS = self.Cursor.fetchall() # 主键为学号加日期，选出一起进行判断
                    if (xh, xh + date + ".txt") not in xh_txtpathS:
                        try:
                            self.Cursor.execute("insert into users_diary (xh, postdate, txtpath) values (:s, :s, :s)", [xh, date, xh + date + ".txt"])
                            self.DB.commit()
                        except:
                            self.DB.rollback()
                    return jsonify({"result": "修改成功", "content": body})
                else: # 登陆非本人，则将该段文字返回其textarea
                    return jsonify({ "result":"修改失败", "content":"此为该用户隐私，您无权修改"})
            else:
                return redirect("/errormsg/1")

    def __del__(self):
        self.Cursor.close()
        self.DB.close()

class StudentInfor(views.View):
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()
        self.get = StudentIndex()
        self.Form = StudentinforClass()
        self.all_fields = ['xh', 'xm', 'sex', 'mz', 'id', 'birthday', 'dept', 'major', 'class',
                      'phone', 'mail', 'type', 'comedate', 'years', 'address', 'domitory']

    def copy_form(self):
        self.Cursor.execute("select * from student_infor where xh = :s", [request.args.get("xh")])
        infor_tuple = self.Cursor.fetchone()
        self.Form.Xh.data = infor_tuple[0]
        self.Form.Xm.data = infor_tuple[1]
        self.Form.Sex.data = infor_tuple[2]
        self.Form.Mz.data = infor_tuple[3]
        self.Form.Id.data = infor_tuple[4]
        self.Form.Birthday.data = infor_tuple[5]
        self.Form.Dept.data = infor_tuple[6]
        self.Form.Major.data = infor_tuple[7]
        self.Form.Class.data = infor_tuple[8]
        self.Form.Phone.data = infor_tuple[9]
        self.Form.Mail.data = infor_tuple[10]
        self.Form.Type.data = infor_tuple[11]
        self.Form.Comedate.data = infor_tuple[12]
        self.Form.Years.data = infor_tuple[13]
        self.Form.Address.data = infor_tuple[14]
        self.Form.Domitory.data = infor_tuple[15]
        self.avatarname = infor_tuple[16]

    def check_permission(self, user):
        self.Cursor.execute("select permission from MODIFY_INFOR_PERMISSION where xh = :s", [user])
        return self.Cursor.fetchone()[0]

    def get_postsql(self):
        if self.Form.Avatar.data.filename:  # 上传头像文件
            RE = ".*(\..*)$"
            end = re.findall(RE, self.Form.Avatar.data.filename)[0]
            randomstring = ''.join(
                random.sample('zyxwvutsrqponmlkjihgfedcba%ZAQWESDFYRUIOOMJ', 10)
            )  # 在上述字符中随机10个作为文件名以防浏览器缓存的直接调取
            filename = randomstring + end
            self.Cursor.execute("select image from student_infor where xh = :s", [request.args.get("xh")])  # 查询原文件名
            img = self.Cursor.fetchone()[0]
            if img != "default.jpg":
                os.remove(os.path.join(current_app.config["DOWNLOADPATHS"], img))  # 删除原文件
                self.Form.Avatar.data.save(os.path.join(current_app.config["DOWNLOADPATHS"], filename))  # 存取新文件
            else:
                self.Form.Avatar.data.save(os.path.join(current_app.config["DOWNLOADPATHS"], filename))
            # 带有文件修改的sql
            sql = "update student_infor set xm='%s',sex='%s',mz='%s',id='%s',birthday='%s',dept='%s',major='%s',class='%s',phonenumber='%s',mail='%s',type='%s'," \
                  "comedate='%s',years=%s, address='%s',domitory='%s',image='%s' where xh = '%s'" % (
                  self.Form.Xm.data, self.Form.Sex.data, self.Form.Mz.data, self.Form.Id.data,
                  self.Form.Birthday.data, self.Form.Dept.data, self.Form.Major.data, self.Form.Class.data,
                  self.Form.Phone.data, self.Form.Mail.data, self.Form.Type.data,
                  self.Form.Comedate.data, self.Form.Years.data, self.Form.Address.data, self.Form.Domitory.data,
                  filename, request.args.get("xh"))
        else:
            sql = "update student_infor set xm='%s',sex='%s',mz='%s',id='%s',birthday='%s',dept='%s',major='%s',class='%s',phonenumber='%s',mail='%s',type='%s'," \
                  "comedate='%s',years=%s, address='%s',domitory='%s' where xh = '%s'" % (
                  self.Form.Xm.data, self.Form.Sex.data, self.Form.Mz.data, self.Form.Id.data,
                  self.Form.Birthday.data, self.Form.Dept.data, self.Form.Major.data, self.Form.Class.data,
                  self.Form.Phone.data, self.Form.Mail.data, self.Form.Type.data,
                  self.Form.Comedate.data, self.Form.Years.data, self.Form.Address.data, self.Form.Domitory.data,
                  request.args.get("xh"))
        return sql

    def toNone_and_setNull(self):
        self.Cursor.execute("select image from student_infor where xh = :s",
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
                if request.method == "GET":  # GET请求
                    permission = self.check_permission(request.args.get("xh"))
                    self.copy_form()
                    if self.avatarname == "default.jpg":  # 是否为刚添加的用户
                        first_time = 1
                    else:
                        first_time = 0
                    if check_result == 0:  # 管理员进入
                        self.Cursor.execute("select xm from employee_infor where xh = :s", [session["user"]])
                        proxy_name = self.Cursor.fetchone()[0]
                        return render_template("infor.html", proxy=proxy_name, modify=1, name=self.Form.Xh.data, realname=self.Form.Xm.data,
                                               form=self.Form, all_fields=self.all_fields, avatar=self.avatarname, first=first_time, identity="student")
                    else:  # 本人进入
                        return render_template("infor.html", proxy="", modify=permission, name=self.Form.Xh.data, realname=self.Form.Xm.data,
                                               form=self.Form, all_fields=self.all_fields, avatar=self.avatarname, first=first_time, identity="student")
                else:  # POST请求
                    permission = self.check_permission(request.args.get("xh"))
                    if check_result == 0: # 管理员
                        self.Cursor.execute("select xm from employee_infor where xh = :s", [session["user"]])
                        proxy_name = self.Cursor.fetchone()[0]
                        self.Cursor.execute("select xh, xm from student_infor where xh = :s",
                                            [request.args.get("xh")])
                        xh_xm = self.Cursor.fetchone()
                        if self.Form.validate_on_submit() and self.Form.Xh.data == "":
                            sql = self.get_postsql() # 调用getsql方法处理是否进行文件上传，得到对应的sql语句
                            try:
                                self.Cursor.execute(sql)
                                self.DB.commit()
                            except:
                                self.Cursor.execute("select image from student_infor where xh = :s", [request.args.get("xh")])
                                self.avatarname = self.Cursor.fetchone()[0]
                                self.DB.rollback()
                                return render_template("infor.html", proxy=proxy_name, modify=1,
                                                       name=xh_xm[0], realname=xh_xm[1],
                                                       form=self.Form, all_fields=self.all_fields,
                                                       errormsg="修改失败，请仔细查看学号冲突", avatar=self.avatarname, identity="student")
                            else: # sql和收回权限没有出现错误，就get当前url
                                return redirect("/student/information?xh=%s" % (request.args.get("xh")))

                        else: # 验证器出现问题
                            toNone = self.toNone_and_setNull()
                            if self.avatarname == "default.jpg":
                                first_time = 1
                            else:
                                first_time = 0
                            return render_template("infor.html", proxy=proxy_name, modify=1, name=xh_xm[0], realname=xh_xm[1], toNone=toNone,
                                                   form=self.Form, all_fields=self.all_fields, errormsg="学号不可更改且请按表单要求输入", first=first_time, avatar=self.avatarname, identity="student")
                    else: # 本人
                        self.Cursor.execute("select xh, xm from student_infor where xh = :s",
                                            [request.args.get("xh")])
                        xh_xm = self.Cursor.fetchone()
                        if permission == 0: # 无修改权限
                            self.copy_form()
                            return render_template("infor.html", proxy="", modify=permission, name=xh_xm[0], realname=xh_xm[1],
                                                   form=self.Form, all_fields=self.all_fields, errormsg="您无权限更改信息", avatar=self.avatarname, identity="student")
                        else:
                            if self.Form.validate_on_submit() and self.Form.Xh.data == "": # 不可更改学号，因此能够修改信息的条件就是学号不为空并且表单认证完成
                                try:
                                    sql = self.get_postsql()
                                    # 用户获取权限后仅供成功修改一次
                                    self.Cursor.execute("update modify_infor_permission set permission = 0 where xh = :s",
                                                        [request.args.get("xh")])
                                    self.Cursor.execute(sql)
                                    self.DB.commit()
                                except:
                                    self.Cursor.execute("select image from student_infor where xh = :s", [request.args.get("xh")])
                                    self.avatarname = self.Cursor.fetchone()[0]
                                    if self.avatarname == "default.jpg":
                                        first_time = 1
                                    else:
                                        first_time = 0
                                    self.DB.rollback()
                                    return render_template("infor.html", proxy="", modify=permission,
                                                           name=self.Form.Xh.data, realname=self.Form.Xm.data,
                                                           form=self.Form, all_fields=self.all_fields, first=first_time,
                                                           errormsg="修改失败，请稍后重试", avatar=self.avatarname, identity="student")
                                else: # sql和收回权限没有出现错误，就get当前url
                                    return redirect("/student/information?xh=%s" % (request.args.get("xh"),))

                            else: # 验证器出现问题
                                toNone = self.toNone_and_setNull()
                                if self.avatarname == "default.jpg":
                                    first_time = 1
                                else:
                                    first_time = 0
                                return render_template("infor.html", proxy="", modify=permission, name=xh_xm[0], realname=xh_xm[1], toNone=toNone,
                                                       form=self.Form, all_fields=self.all_fields, errormsg="学号不可更改，请按表单要求输入",
                                                       avatar=self.avatarname, first=first_time, identity="student")
        else:
            return redirect("/errormsg/1")

    def __del__(self):
        self.Cursor.close()
        self.DB.close()


class StudentCourse(views.View):
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()
        self.get = StudentIndex()

    def dispatch_request(self):
        if session.get("user"):
            check_result = self.get.check_identity()
            if isinstance(check_result, str):
                return redirect(check_result)
            else:
                realname = self.Cursor.execute("select xm from student_infor where xh = :s", [request.args.get("xh")]).fetchone()[0]
                normal_exam_grade = self.Cursor.execute("select EXAMGRADE, NORMALGRADE from sc where xh = :s order by kh", [request.args.get("xh")]).fetchall()
                normal_exam_qz = self.Cursor.execute("select normalqz, examqz, examdate from course where kh in (select kh from sc where xh = :s) order by kh", [request.args.get("xh")]).fetchall()
                grades = list()
                ispasses = list()
                date = list()
                print(normal_exam_qz)
                print(normal_exam_grade)
                final_grade = self.Cursor.execute("select finalgrade from sc where xh = :s order by kh", [request.args.get("xh")]).fetchall()
                print(final_grade)
                for i in range(len(normal_exam_qz)):
                    if final_grade[i][0]:
                        grade = final_grade[i][0]
                        ispasses.append("及格" if grade >= 60 else "不及格")
                    else:
                        if normal_exam_qz[i][0] and normal_exam_qz[i][1] and normal_exam_grade[i][1] and normal_exam_grade[i][0]:
                            grade = normal_exam_grade[i][0] * normal_exam_qz[i][0] + normal_exam_grade[i][1] * normal_exam_qz[i][1]
                            ispasses.append("及格" if grade >= 60 else "不及格")
                            grade = str(grade)
                        else:
                            grade = "未录入"
                            ispasses.append("未录入")
                    grades.append(grade)
                    if normal_exam_qz[i][2]:
                        date.append(normal_exam_qz[i][2].replace('#', '.', 3))
                    else:
                        date.append("")

                courses = self.Cursor.execute("select to_char(course.kh, '000000'), kname, khours, knature, kcredit, examnature, testtype from course, sc where course.kh = sc.kh and xh = :s order by sc.kh", [request.args.get("xh")]).fetchall()
                print(courses)
                result_list = list()
                for i in range(len(courses)):
                    temp = list()
                    temp.append(courses[i][0])
                    temp.append(courses[i][1])
                    temp.append(courses[i][2])
                    temp.append(courses[i][3])
                    temp.append(courses[i][4])
                    temp.append(grades[i])
                    temp.append(courses[i][5])
                    temp.append(courses[i][6])
                    temp.append(ispasses[i])
                    temp.append(date[i])
                    result_list.append(temp)
                if check_result == 0:
                    return render_template("course.html", proxy=session["user"], identity="student", realname=realname, name=request.args.get("xh"), courses=result_list)
                else:
                    return render_template("course.html", proxy="", identity="student", realname=realname, name=request.args.get("xh"), courses=result_list)
        else:
            return redirect("/errormsg/1")

    def __del__(self):
        self.Cursor.close()
        self.DB.close()

class StudentSC(views.View):
    def __init__(self):
        self.DB = current_app.config["DATABASE"].connection()
        self.Cursor = self.DB.cursor()

    def dispatch_request(self):
        if session.get('user'):
            admins = self.Cursor.execute("select xh from admin_ where identity = 0").fetchall()
            students = self.Cursor.execute("select xh from admin_ where identity = 1").fetchall()
            teachers = self.Cursor.execute("select xh from admin_ where identity = 2").fetchall()
            self.Cursor.execute(
                "select kh, kname, khours, knature, kcredit, kamount, testtype, xm from course, employee_infor where xh = kteacher")
            selectcourses = list()
            sc_tuple = self.Cursor.fetchall()
            for i in sc_tuple:
                selectcourse = list()
                selectcourse.append(i[0])
                selectcourse.append(i[1])
                selectcourse.append(i[2])
                selectcourse.append(i[3])
                selectcourse.append(i[4])
                selectcourse.append(
                    i[5] - int(self.Cursor.execute("select count(*) from sc where kh = :s", [i[0]]).fetchone()[0]))
                selectcourse.append(i[6])
                selectcourse.append(i[7])
                selectcourse.append(1 if (i[0],) in self.Cursor.execute("select kh from sc where xh = :s",
                                                                        [session["user"]]).fetchall() else 0)
                selectcourses.append(selectcourse)
            print(selectcourses)
            if (session["user"],) in admins:
                xm = self.Cursor.execute("select xm from employee_infor where xh = :s", [session["user"]]).fetchone()[0]
                return render_template("selectcourse.html", proxy="", name=session["user"], identity="admin",
                                       realname=xm, selectcourses=selectcourses)
            elif (session["user"],) in students:
                xm = self.Cursor.execute("select xm from student_infor where xh = :s", [session["user"]]).fetchone()[0]
                if request.method == "GET":
                    return render_template("selectcourse.html", proxy="", name=session["user"], identity="student", realname=xm, selectcourses=selectcourses)
                else:
                    if request.form.get("type")=="add":
                        if int(self.Cursor.execute("select count(*) from sc where kh = :s", [request.form.get("kh")]).fetchone()[0]) < self.Cursor.execute("select kamount from course where kh = :s", [request.form.get("kh")]).fetchone()[0]:
                            try:
                                self.Cursor.execute("insert into sc (xh, kh, examnature) values (:s, :s, :s)", [request.form.get("xh"), request.form.get("kh"), "正常考试"])
                                self.DB.commit()
                            except:
                                self.DB.rollback()
                                return "添加失败"
                            else:
                                return "添加成功"
                        else:
                            return "添加失败，人数已满"
                    else:
                        try:
                            self.Cursor.execute("delete from sc where xh = :s and kh = :s", [request.form.get("xh"), request.form.get("kh")])
                            self.DB.commit()
                        except:
                            self.DB.rollback()
                            return "退选失败"
                        else:
                            return "退选成功"
            else:
                xm = self.Cursor.execute("select xm from employee_infor where xh = :s", [session["user"]]).fetchone()[0]
                return render_template("selectcourse.html", proxy="", name=session["user"], identity="teacher",
                                       realname=xm, selectcourses=selectcourses)
        else:
            return redirect("/errormsg/1")
    def __del__(self):
        self.Cursor.close()
        self.DB.close()