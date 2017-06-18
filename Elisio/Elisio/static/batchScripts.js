$(document).ready(function () {
    $("#clearCurrentBatchButton").click(function () {
        $.getJSON("/json/clearsession", function (result) {
            $("#currentBatchTable").remove();
        });
    });
    $(".deleteVerseFromCurrentBatch").click(function () {
        var hash = $(this).attr("alt");
        $.getJSON("/json/deleteverse/" + hash, function (result) {
            $("#"+hash).remove();
        });
    });
});
