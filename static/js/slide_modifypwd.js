$("#special").click( function() {
                $("#slide_box").slideDown(500);
                $("#slide_cover").slideDown(200);
                setTimeout(function(){
                    $("#slide_head").css("display", "");
                    $("#slide_body").css("display", "");
                    $("#slide_head").css("animation", "fadeIn 1s");
                    $("#slide_head").css("-webkit-animation", "fadeIn 1s");
                    $("#slide_body").css("animation", "fadeIn 1s");
                    $("#slide_body").css("-webkit-animation", "fadeIn 1s");
                }, 490);
            })
            //点击滑出淡入的js

$("#slide_close").click(function() {
    $("#msg").text("");
    $("#slide_opwd").val("");
    $("#slide_npwd").val("");
    $("#slide_cpwd").val("");
    $("#slide_head").css("animation", "fadeOut 0.5s");
    $("#slide_head").css("-webkit-animation", "fadeOut 0.5s");
    $("#slide_body").css("animation", "fadeOut 0.5s");
    $("#slide_body").css("-webkit-animation", "fadeOut 0.5s");
    setTimeout(function(){
        $("#slide_head").css("display", "none");
        $("#slide_body").css("display", "none");
        $("#slide_box").slideUp(500);
        $("#slide_cover").slideUp(200);
    }, 490);
})
$("#slide_cover").click(function() {
    $("#slide_close").trigger("click");
})
            //点击滑入淡出的js
$("#slide_submit").click(function() {
    var proxy = "False";
    var user = ""
    if ($("#opwd_label").text() == "您的密码：")
    {
        proxy = "True";
        user = getUrlParam("xh");
    }
    $("#msg").text("正在提交中...");
    $.ajax ({
        url:"/modifypwd.action",
        type: "post",
        data: { "oldpwd": $("#slide_opwd").val(), "newpwd": $("#slide_npwd").val(), "confirmpwd": $("#slide_cpwd").val(), "proxy":proxy, "user":user },
        success: function(response) {
            setTimeout(function() { $("#msg").text(response); }, 200);
            if (response.substring(response.length - 7) == "即将关闭..."){
                setTimeout(function() {
                $("#slide_close").trigger("click");
                 }, 2000);
                }
        }
    })
})
            //提交数据的ajax