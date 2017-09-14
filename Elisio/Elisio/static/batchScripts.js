function getCookie(c_name) {
    if (document.cookie.length > 0) {
        var c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            var c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

$(function () {
    $.ajaxSetup({
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });
});

function resetBatchField(objects) {
    objects.empty();
    objects.append($("<option />").val("All").text("All"));
    return objects;
}

function getAllAuthors() {
    var objects = $(".authorBatchField");
    $.getJSON("/json/authors/", function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.short_name));
        });
        $('.authorBatchField option:first-child').attr("selected", "selected");
    });
}

function saveCurrentBatch() {
    $.post("/json/batch/save/", function (result) {
        alert("batch saved");
    });
}

function saveCurrentBatchItems() {
    var arr = [];
    $(".criterium").each(function () {
        var queryType = "";
        var queryObj = 0;
        var author = $(this).find(".authorBatchField").val();
        if (author === 'All') {
            queryType = "all";
        }
        else {
            var opus = $(this).find(".opusBatchField").val();
            if (opus === 'All') {
                queryType = "author";
                queryObj = author;
            } else {
                var book = $(this).find(".bookBatchField").val();
                if (book === 'All') {
                    queryType = "opus";
                    queryObj = opus;
                } else {
                    var poem = $(this).find(".poemBatchField").val();
                    if (poem === 'All') {
                        queryType = "book";
                        queryObj = book;
                    }
                    else {
                        queryType = "poem";
                        queryObj = poem;
                    }
                }
            }
        }
        var extra = {
            type: queryType,
            id: queryObj
        };
        var relationField = $(this).find(".relationBatchField");
        if (relationField.css("display") !== "none") {
            extra.relation = relationField.val();
        }
        arr.push(extra);
    });
    $.ajax({
        url: "/json/batchitem/save/",
        type: "POST",
        data: JSON.stringify(arr),
        success: function (data, status, xhr) {

        }
    });
}

function getAllBatches() {
    var objects = $("#existingBatchesTable");
    var content = "";
    $.when($.getJSON("/json/batches/", function (result) {
        $.each(result, function () {
            content += "<tr id=batch" + this.id + ">";
            content += "<td>" + this.name + "</td>";
            content += "<td>" + this.timing + "</td>";
            content += "<td>" + this.itemsAtCreation + "</td>";
            content += "<td>" + this.itemsNow + "</td>";
            if (this.scans && this.scans.number > 0) {
                content += "<td>" + this.scans.recent + "</td>";
            }
            else {
                content += "<td>N/A</td>";
            }
            content += "<td><img src='/static/delete.png' class='runBatch' alt='" + this.id + "' height='16' width='16'/></td>";
            content += "<td><img src='/static/delete.png' class='deleteBatch' alt='" + this.id + "' height='16' width='16'/></td>";
            content += "</tr>";
        });
        objects.append(content);
    })).then(function () {
        $(".deleteBatch").click(function () {
            var id = $(this).attr("alt");
            $.ajax({
                url: '/json/batch/delete/' + id,
                type: 'DELETE',
                success: function (response) {
                    $("#batch" + id).remove();
                },
                complete: function (response, text) {
                    alert("batch deleted ?" + response.status);
                }
            });
        });
        $(".runBatch").click(function () {
            var id = $(this).attr("alt");
            $.ajax({
                url: '/json/batch/run/' + id,
                type: 'POST',
                complete: function (response, text) {
                    alert("batch run:" + response.status);
                }
            });
        });
    });
}

function getAllOpera(item) {
    var row = $(item).parent().parent();
    var opus = row.find(".opusBatchField");
    var objects = resetBatchField(opus);
    if (item.value !== "All") {
        $.getJSON("/json/author/" + item.value, function (result) {
            $.each(result, function () {
                objects.append($("<option />").val(this.pk).text(this.fields.full_name));
            });
            opus.find('option:first-child').attr("selected", "selected");
        });
    }
    resetBatchField(row.find(".bookBatchField"));
    resetBatchField(row.find(".poemBatchField"));
}

function getAllBooks(item) {
    var row = $(item).parent().parent();
    var book = row.find(".bookBatchField");
    var objects = resetBatchField(book);
    if (item.value !== "All") {
        $.getJSON("/json/opus/" + item.value, function (result) {
            $.each(result, function () {
                objects.append($("<option />").val(this.pk).text(this.fields.number));
            });
            book.find('option:first-child').attr("selected", "selected");
        });
    }
    resetBatchField(row.find(".poemBatchField"));
}

function getAllPoems(item) {
    var row = $(item).parent().parent();
    var poem = row.find(".poemBatchField");
    var objects = resetBatchField(poem);
    if (item.value !== "All") {
        $.getJSON("/json/book/" + item.value, function (result) {
            $.each(result, function () {
                objects.append($("<option />").val(this.pk).text(this.fields.number));
            });
            poem.find('option:first-child').attr("selected", "selected");
        });
    }
}

$(document).ready(function () {
    $("#clearCurrentBatchButton").click(function () {
        $.getJSON("/json/batch/clearcurrentsession", function (result) {
            $("#currentBatchTable").remove();
        });
    });

    $(".deleteVerseFromCurrentBatch").click(function () {
        var hash = $(this).attr("alt");
        $.getJSON("/json/batch/deleteverse/" + hash, function (result) {
            $("#"+hash).remove();
        });
    });

    getAllAuthors();
    getAllBatches();

    $(".authorBatchField").change(function () {
        getAllOpera(this);
    });

    $(".opusBatchField").change(function () {
        getAllBooks(this);
    });

    $(".bookBatchField").change(function () {
        getAllPoems(this);
    });

    $("#saveCurrentBatchButton").click(function () {
        saveCurrentBatch();
    });

    $("#saveitems").click(function () {
        saveCurrentBatchItems();
    });
});
