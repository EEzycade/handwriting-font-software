function toggle_dark(check) {
    if(check.checked) {
        $('body').addClass('theme-dark');
        setCookie("dark-mode", "true", 365);
    } else {
        $('body').removeClass('theme-dark');
        setCookie("dark-mode", "false", 365);
    }
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function checkCookie() {
    var darkMode = getCookie("dark-mode");
    if (darkMode == "") {
        darkMode = "false";
        setCookie("dark-mode", darkMode, 365);
    } else if (darkMode == "true") {
        $('body').addClass('theme-dark');
        $('#dark-mode-switch').prop('checked', true);
    }
}