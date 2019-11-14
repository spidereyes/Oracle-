function redirectto() {
    location.href = window.location.protocol + "//" + window.location.host + "/";
}

function addpoint() {
    document.getElementById("msg").innerText += "..";
}

var i = 3;
function add() {
    if (i == 0) return;
    addpoint();
    setTimeout(add, 1000);
    i--;
}
add();
setTimeout(redirectto, 3500);