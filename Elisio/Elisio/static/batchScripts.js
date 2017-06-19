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
    $.getJSON("/json/batch/save/", function (result) {
        alert("batch saved");
    });
}

function getAllBatches() {
    var objects = $("#existingBatchesTable");
    var content = "";
    $.when($.getJSON("/json/batches/", function (result) {
        $.each(result, function () {
            content += "<tr><td>" + this.fields.timing + "</td></tr>";
            objects.append(content);
        });
    }));
}

function getAllOpera(key) {
    var objects = resetBatchField("#opusBatchField");
    if (key !== "All") {
        $.when($.getJSON("/json/author/" + key, function (result) {
            $.each(result, function () {
                objects.append($("<option />").val(this.pk).text(this.fields.full_name));
            });
            $('#opusBatchField option:first-child').attr("selected", "selected");
        }));
    }
    resetBatchField("#bookBatchField");
    resetBatchField("#poemBatchField");
}

function getAllBooks(key) {
    var objects = resetBatchField("#bookBatchField");
    if (key !== "All") {
        $.when($.getJSON("/json/opus/" + key, function (result) {
            $.each(result, function () {
                objects.append($("<option />").val(this.pk).text(this.fields.number));
            });
            $('#bookBatchField option:first-child').attr("selected", "selected");
        }));
    }
    resetBatchField("#poemBatchField");
}

function getAllPoems(key) {
    var objects = resetBatchField("#poemBatchField");
    if (key !== "All") {
        $.when($.getJSON("/json/book/" + key, function (result) {
            $.each(result, function () {
                objects.append($("<option />").val(this.pk).text(this.fields.number));
            });
            $('#poemBatchField option:first-child').attr("selected", "selected");
        }));
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
