$(document).ready(function () {
    $("#syncFiles").click(function () {
        $.getJSON("/json/admin/syncFiles", function (result) {
            alert("done syncing files");
        });
    });
    $("#syncDb").click(function () {
        $.getJSON("/json/admin/syncDb", function (result) {
            alert("done syncing db");
        });
    });
});
