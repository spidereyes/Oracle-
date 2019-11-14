var a = document.getElementById("show_user").innerText.length;
var result = a * 12 + 30;
document.getElementById("show_user").style.left = "calc(100% - " + result + "px)";

function getUrlParam(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
        var r = window.location.search.substr(1).match(reg);  //匹配目标参数
        if (r != null) return unescape(r[2]); return null; //返回参数值
    }

function fulldate(y, m, d)
{
    if(m.length == 1 && d.length ==  1) {
        return y + "#0" + m + "#0" + d;
    }
    else if(m.length == 1&&d.length == 2) {
        return y + "#0" + m + "#" + d;
    }
    else if(m.length == 2&&d.length == 1) {
        return y + "#" + m + "#0" + d;
    }
    else{
        return y + "#" + m + "#" + d;
    }
}

function delete_confirm()
{
    var a = confirm("删除是不可恢复的，你确认要删除吗？");
    if(a)
        return true;
    else
        return false;
}