from flask import Flask
from config import Config
from Blueprints.Manager import Loginbp, Login, Modifypwd, GetPost
from Blueprints.Teacher import Teacherbp, TeacherIndex, Teacherinfor, Teachercourse
from Blueprints.Admin import Adminbp, AdminIndex, AdminUsers, AdminSystem, AdminInfor
from Blueprints.Student import Studentbp, StudentIndex, DiaryPostView, StudentInfor, StudentCourse, StudentSC
app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(Loginbp)
app.register_blueprint(Teacherbp)
app.register_blueprint(Studentbp)
app.register_blueprint(Adminbp)

app.add_url_rule("/", view_func=Login.as_view("loginview"), methods=["POST", "GET"])
app.add_url_rule("/student/index", view_func=StudentIndex.as_view("studentindex"), methods=["POST", "GET"])
app.add_url_rule("/teacher/index", view_func=TeacherIndex.as_view("teacherindex"), methods=["POST", "GET"])
app.add_url_rule("/admin/index", view_func=AdminIndex.as_view("adinindex"), methods=["POST", "GET"])
app.add_url_rule("/managediary", view_func=DiaryPostView.as_view("diarypostview"), methods=["POST", "GET"])
app.add_url_rule("/modifypwd.action", view_func=Modifypwd.as_view("modifypwd"), methods=["POST", "GET"])
app.add_url_rule("/student/information", view_func=StudentInfor.as_view("studentinfor"), methods=["GET", "POST"])
app.add_url_rule("/student/course", view_func=StudentCourse.as_view("studentcourse"), methods=["GET"])
app.add_url_rule("/student/get/post", view_func=GetPost.as_view("getpost"), methods=["GET", "POST"])
app.add_url_rule("/student/selectcourse", view_func=StudentSC.as_view("studentsc"), methods=["GET", "POST"])
app.add_url_rule("/teacher/course", view_func=Teachercourse.as_view("teachercourse"), methods=["GET", "POST"])
app.add_url_rule("/admin/information", view_func=AdminInfor.as_view("admininfor"), methods=["GET", "POST"])
app.add_url_rule("/teacher/information", view_func=Teacherinfor.as_view("teacherinfor"), methods=["GET", "POST"])
app.add_url_rule("/admin/user", view_func=AdminUsers.as_view("adminusers"), methods=["GET", "POST"])
app.add_url_rule("/admin/system", view_func=AdminSystem.as_view("adminsystem"), methods=["GET", "POST"])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=80)

# flask指令
'''
cd G:\Flask-Oracle
set FLASK_APP=run
set FLASK_ENV=development
flask run

'''
# shell指令
'''
cd G:\新的
pipenv shell
cd G:\Flask-Oracle
python run.py

'''


# from flask import Flask, session, request, Response
# import urllib
# import urllib.parse
# app = Flask(__name__)
# app.secret_key = '*********************' # 不可知
# def FLAG():
#     return 'FLAG_is_here_but_i_wont_show_you'  # 不可知
# def trigger_event(event):
#     session['log'].append(event)
#     if len(session['log']) > 5: session['log'] = session['log'][-5:]
#     if type(event) == type([]):
#         request.event_queue += event
#     else:
#         request.event_queue.append(event)
# def get_mid_str(haystack, prefix, postfix=None): ## 筛出prefix和postfix之间的字符串
#     haystack = haystack[haystack.find(prefix)+len(prefix):]
#     if postfix is not None:
#         haystack = haystack[:haystack.find(postfix)]
#     return haystack
# class RollBackException: pass
# def execute_event_loop():
#     valid_event_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789:;#')
#     resp = None
#     while len(request.event_queue) > 0:
#         event = request.event_queue[0] # `event` is something like "action:ACTION;ARGS0#ARGS1#ARGS2......"
#         request.event_queue = request.event_queue[1:]
#         if not event.startswith(('action:', 'func:')): # 只能以action或者func开头
#             continue
#         for c in event: # 如果此次操作字符串中存在非法字符则跳出循环
#             if c not in valid_event_chars:
#                 break
#         else:
#             is_action = event[0] == 'a' # 注意这里是 event[0] == 'a'是判断
#             action = get_mid_str(event, ':', ';')  ## 选出:和;之间的内容
#             args = get_mid_str(event, action+';').split('#') ## 将;后面的内容以#为界线划为列表
#             try:
#                 event_handler = eval(action + ('_handler' if is_action else '_function'))
#                 ret_val = event_handler(args)
#             except RollBackException:
#                 if resp is None: resp = ''
#                 resp += 'ERROR! All transactions have been cancelled. <br />'
#                 resp += '<a href="./?action:view;index">Go back to index.html</a><br />'
#                 session['num_items'] = request.prev_session['num_items']
#                 session['points'] = request.prev_session['points']
#                 break
#             except Exception as e:
#                 if resp is None: resp = ''
#                 #resp += str(e) # only for debugging
#                 continue
#             if ret_val is not None:
#                 if resp is None: resp = ret_val
#                 else: resp += ret_val
#     if resp is None or resp == '': resp = ('404 NOT FOUND', 404)
#     session.modified = True
#     print(resp)
#     return resp
# @app.route('/')
# def entry_point():
#     querystring = urllib.parse.unquote(str(request.query_string, encoding='utf-8'))
#     request.event_queue = []
#     if querystring == '' or (not querystring.startswith('action:')) or len(querystring) > 100:
#         querystring = 'action:index;False#False'
#     if 'num_items' not in session:
#         session['num_items'] = 0
#         session['points'] = 3
#         session['log'] = []
#     request.prev_session = dict(session)
#     trigger_event(querystring)
#     return execute_event_loop()
# # handlers/functions below --------------------------------------
# def view_handler(args):
#     page = args[0]
#     html = ''
#     html += '[INFO] you have {} diamonds, {} points now.<br />'.format(session['num_items'], session['points'])
#     if page == 'index':
#         html += '<a href="./?action:index;True%23False">View source code</a><br />'
#         html += '<a href="./?action:view;shop">Go to e-shop</a><br />'
#         html += '<a href="./?action:view;reset">Reset</a><br />'
#     elif page == 'shop':
#         html += '<a href="./?action:buy;1">Buy a diamond (1 point)</a><br />'
#     elif page == 'reset':
#         del session['num_items']
#         html += 'Session reset.<br />'
#     html += '<a href="./?action:view;index">Go back to index.html</a><br />'
#     return html
# def index_handler(args):
#     bool_show_source = str(args[0])
#     bool_download_source = str(args[1])
#     if bool_show_source == 'True':
#         source = open('eventLoop.py', 'r')
#         html = ''
#         if bool_download_source != 'True':
#             html += '<a href="./?action:index;True%23True">Download this .py file</a><br />'
#             html += '<a href="./?action:view;index">Go back to index.html</a><br />'
#         for line in source:
#             if bool_download_source != 'True':
#                 html += line.replace('&','&amp;').replace('\t', '&nbsp;'*4).replace(' ','&nbsp;').replace('<', '&lt;').replace('>','&gt;').replace('\n', '<br />')
#             else:
#                 html += line
#         source.close()
#         if bool_download_source == 'True':
#             headers = {}
#             headers['Content-Type'] = 'text/plain'
#             headers['Content-Disposition'] = 'attachment; filename=serve.py'
#             return Response(html, headers=headers)
#         else:
#             return html
#     else:
#         trigger_event('action:view;index')
# def buy_handler(args):
#     num_items = int(args[0])
#     if num_items <= 0: return 'invalid number({}) of diamonds to buy<br />'.format(args[0])
#     session['num_items'] += num_items
#     trigger_event(['func:consume_point;{}'.format(num_items), 'action:view;index'])
# def consume_point_function(args):
#     point_to_consume = int(args[0])
#     if session['points'] < point_to_consume: # 购买水晶小于session中拥有的点数则报错
#         raise RollBackException()
#     session['points'] -= point_to_consume
# def show_flag_function(args):
#     flag = args[0]
#     #return flag # GOTCHA! We noticed that here is a backdoor planted by a hacker which will print the flag, so we disabled it.
#     return 'You naughty boy! ;) <br />'
# def get_flag_handler(args):
#     if session['num_items'] >= 5:
#         trigger_event('func:show_flag;' + FLAG()) # show_flag_function has been disabled, no worries
#     trigger_event('action:view;index')
# if __name__ == '__main__':
#     app.run(debug=True)