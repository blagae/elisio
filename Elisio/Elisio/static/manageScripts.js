$(document).ready(function () {
    $("#syncFilesButton").click(function () {
        $.getJSON("/json/admin/sync/files", function (result) {
            alert("done syncing files");
        });
    });
    $("#syncDbButton").click(function () {
        $.getJSON("/json/admin/sync/db", function (result) {
            alert("done syncing db");
        });
    });
});
