function getOpera(key) {
    $.getJSON("/json/author/" + key, function (result) {
        var objects = $("#opus");
        objects.empty();
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.full_name));
        });
    });
}

function getBooks(key) {
    $.getJSON("/json/opus/" + key, function (result) {
        var objects = $("#book");
        objects.empty();
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.number));
        });
    });
}

$(document).ready(function () {

    $("#author").change(function () {
        getOpera(this.value);
    });
    $("#opus").change(function () {
        getBooks(this.value);
    });

});