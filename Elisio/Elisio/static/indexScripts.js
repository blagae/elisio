var maxVerseNumber = 0;

function getOpera(key) {
    var objects = $("#opus");
    objects.empty();
    $.when($.getJSON("/json/author/" + key, function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.full_name));
        });
        $('#opus option:first-child').attr("selected", "selected");
    })).then(function () {
        getBooks($("#opus").val());
    });
}

function getBooks(key) {
    var objects = $("#book");
    objects.empty();
    $.when($.getJSON("/json/opus/" + key, function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.number));
        });
        $('#book option:first-child').attr("selected", "selected");
    })).then(function () { 
        getPoems($("#book").val());
    });
}

function getPoems(key) {
    var objects = $("#poem");
    objects.empty();
    $.when($.getJSON("/json/book/" + key, function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.number));
        });
        $('#poem option:first-child').attr("selected", "selected");
    })).then(function () { 
        getMaxVerseNumber($("#poem").val());
    });
}

function getMaxVerseNumber(key) {
    maxVerseNumber = 0;
    $.getJSON("/json/poem/" + key, function (result) {
        maxVerseNumber = result;
    });
}

function getVerse(poem, verse) {
    var url = "/json/verse/" + poem + "/" + verse;
    $.getJSON(url, function (result) {
        $("#verse").val(result);
    });
}

function validateVerseNumber(val) {
    var regex = /^[0-9]+$/;
    if (!regex.test(val)) {
        $("#warning").text("Voer hier een cijfer in!");
    } else {
        $("#warning").empty();
    };
    if (val > maxVerseNumber) {
        $("#warning").text("Maximum verse number is " + maxVerseNumber);
    }
    return $("#warning").text() == "";
}

$(document).ready(function () {

    $("#author").change(function () {
        getOpera(this.value);
        // new <
        getMaxVerseNumber($("#poem").val());
        // new >
    });
    $("#opus").change(function () {
        getBooks(this.value);
    });
    $("#book").change(function () {
        getPoems(this.value);
    });
    $("#poem").change(function () {
        getMaxVerseNumber(this.value);
    });
    $("#verseNumber").change(function () {
        var validated = validateVerseNumber(this.value);
        if (validated) {
            getVerse($("#poem").val(), this.value);
        }
    });

    $("#author").change();
    $("#opus").change();
    $("#book").change();

});