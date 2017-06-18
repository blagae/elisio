$(document).ready(function () {
    $("#syncFilesButton").click(function () {
        $.getJSON("/json/admin/syncFiles", function (result) {
            alert("done syncing files");
        });
    });
    $("#syncDbButton").click(function () {
        $.getJSON("/json/admin/syncDb", function (result) {
            alert("done syncing db");
        });
    });
});
