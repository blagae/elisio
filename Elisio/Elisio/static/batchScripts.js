$(document).ready(function () {
    $("#clearSession").click(function () {
        $.getJSON("/json/clearsession", function (result) {
            $("#batchTable").remove();
        });
    });
});