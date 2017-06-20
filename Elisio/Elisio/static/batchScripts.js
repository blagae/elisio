function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
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

function resetBatchField(id) {
    var objects = $(id);
    objects.empty();
    objects.append($("<option />").val("All").text("All"));
    return objects;
}

function getAllAuthors() {
    var objects = $("#authorBatchField");
    $.getJSON("/json/authors/", function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.short_name));
        });
        $('#authorBatchField option:first-child').attr("selected", "selected");
    });
}

function saveCurrentBatch() {
    $.post("/json/batch/save/", function (result) {
        alert("batch saved");
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
                content += "<td>" + this.scans.number + "</td>";
                content += "<td>" + this.scans.recent + "</td>";
            }
            else {
                content += "<td>0</td>";
                content += "<td>N/A</td>";
            }
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
    });
}

function getAllOpera(key) {
    var objects = resetBatchField("#opusBatchField");
    if (key !== "All") {
        $.getJSON("/json/author/" + key, function (result) {
            $.each(result, function () {
                objects.append($("<option />").val(this.pk).text(this.fields.full_name));
            });
            $('#opusBatchField option:first-child').attr("selected", "selected");
        });
    }
    resetBatchField("#bookBatchField");
    resetBatchField("#poemBatchField");
}

function getAllBooks(key) {
    var objects = resetBatchField("#bookBatchField");
    if (key !== "All") {
        $.getJSON("/json/opus/" + key, function (result) {
            $.each(result, function () {
                objects.append($("<option />").val(this.pk).text(this.fields.number));
            });
            $('#bookBatchField option:first-child').attr("selected", "selected");
        });
    }
    resetBatchField("#poemBatchField");
}

function getAllPoems(key) {
    var objects = resetBatchField("#poemBatchField");
    if (key !== "All") {
        $.getJSON("/json/book/" + key, function (result) {
            $.each(result, function () {
                objects.append($("<option />").val(this.pk).text(this.fields.number));
            });
            $('#poemBatchField option:first-child').attr("selected", "selected");
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

    $("#authorBatchField").change(function () {
        getAllOpera(this.value);
    });

    $("#opusBatchField").change(function () {
        getAllBooks(this.value);
    });

    $("#bookBatchField").change(function () {
        getAllPoems(this.value);
    });

    $("#saveCurrentBatchButton").click(function () {
        saveCurrentBatch();
    });
});
