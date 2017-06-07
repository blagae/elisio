$(document).ready(function () {
    $("#clearSession").click(function () {
        $.getJSON("/json/clearsession", function (result) {
            $("#batchTable").remove();
        });
    });
    $(".delete").click(function () {
        var hash = $(this).attr("alt");
        $.getJSON("/json/deleteverse/" + hash, function (result) {
            $("#"+hash).remove();
        });
    });
});
