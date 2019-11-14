$(function()
{
    var month_offset = 0;
    function run(offset)
    {
        var Today = new Date(); // 获取当前日期
        var Year = Today.getFullYear(); // 获取当前日期的年
        var Day = Today.getDate();  // 获取当前日期的日
        Today.setMonth(Today.getMonth() + offset); // 把当前日期的月份改为根据偏移量而改变的月份
        var Month = Today.getMonth(); // 获取偏移后的月份
        var month_days = new Array(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
        if(Month == 1){
            if(Year % 4 == 0 && Year % 100 == 0 || Year % 400 == 0) {
                month_days[Month] = 29;
            }
        }// 闰年
        var now_month_days = month_days[Month]; // 获取偏移后月份的总天数
        Today.setDate(1); // 将当前日期改为该月第一天
        var now_month_firstday = Today.getDay(); // 获取第一天位于星期几
        $(".date").empty(); // 清空ul中的内容
        for(var i = 0; i < now_month_firstday; i++) // 1号以前的礼拜不需要赋值给个空li即可
        {
            $(".date").append("<li></li>")
        } 
        for(var i = 1; i <= now_month_days; i++) // 1号以后开始增加含有日期的li标签
        {
             if(offset > 0)
             {
                $(".date").append("<li><font style=\"pointer-events: none; color: #888\">" + i + "</font></li>")
             }
             else if(offset == 0)
             {
                if(i < Day)
                    $(".date").append("<li><font onclick=\"getextarea(this, " + Year + "," + (Month+1) + "," + i + ")\">" + i + "</font></li>")
                else if(i == Day)// 遍历到了当前日期的日时
                    $(".date").append("<li><font id=\"posted\" class=\"today\" onclick=\"getextarea(this, " + Year + "," + (Month+1) + "," + i + ")\">" + i + "</font></li>")
                else
                    $(".date").append("<li><font style=\"pointer-events: none; color: #888\">" + i + "</font></li>")
             }
             else
             {
                    $(".date").append("<li><font onclick=\"getextarea(this, " + Year + "," + (Month+1) + "," + i + ")\">" + i + "</font></li>")
             }
        }
        $("#YandM").text(Year + "年" + (Month+1) + "月") // 标题改为偏移后的年份月份
    }
    run(0); // 从当前月开始执行
    $("#next").click(function(){ // 下一个月，偏移量加一
        month_offset+=1;
        run(month_offset);
    });
    $("#last").click(function(){ // 上一个月，偏移量减一
        month_offset-=1;
        run(month_offset);
    });
}
)

//展示日历js

var day =  new Date()
day.setTime(day.getTime());
var today = fulldate(day.getFullYear().toString(), (day.getMonth() + 1).toString(), day.getDate().toString())
var text = day.getDate().toString();

var pathname = window.location.pathname;
var reg = new RegExp("^/(.+?)/.+$");
var result = reg.exec(pathname)[1]; //路径第一段:student,teacher,admin
function getextarea(obj, y, m, d)
{
    $("#posted").removeAttr("id");
    obj.setAttribute("id", "posted");
    today = fulldate(y.toString(), m.toString(), d.toString());
    $("#hidden_time").val(today);
    $.ajax ({
    url: "/managediary",
    type: "get",
    data: { "xh": getUrlParam("xh"), "date": today, "type": result },
    success: function(response) {
        $("#edit").val(response);
    }
    })
}
//点击日历的日期获取日记的ajax

$("#edit_submit").click(function() {
    $.ajax
    ({
        url: "/managediary",
        type: "post",
        data:
        { "body": $("#edit").val(), "xh": getUrlParam("xh"),
            "date":function()
            {
                var temp = $("#hidden_time").val();
                if(temp) { return temp; } else { return today; }
            },
            "type": result
        },
        dataType: "json",
        success: function(response) {
            alert(response["result"]);
            $("#edit").val(response["content"]);
        }
    })
})

//点击日记提交的ajax