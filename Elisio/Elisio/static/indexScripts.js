var maxVerseNumber = 0;

function getOpera(key, op, bk, po) {
    var objects = $("#opus");
    objects.empty();
    $.when($.getJSON("/json/author/" + key, function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.full_name));
        });
        if (typeof op === "undefined")
            $('#opus option:first-child').attr("selected", "selected");
        else
            $("#opus").val(op);
    })).then(function () {
        getBooks($("#opus").val(), bk, po);
    });
}

function getBooks(key, bk, po) {
    var objects = $("#book");
    objects.empty();
    $.when($.getJSON("/json/opus/" + key, function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.number));
        });
        if (typeof bk === "undefined")
            $('#book option:first-child').attr("selected", "selected");
        else
            $("#book").val(bk);
    })).then(function () {
        getPoems($("#book").val(), po);
    });
}

function getPoems(key, po) {
    var objects = $("#poem");
    objects.empty();
    $.when($.getJSON("/json/book/" + key, function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.number));
        });
        if (typeof po === "undefined")
            $('#poem option:first-child').attr("selected", "selected");
        else
            $("#poem").val(po);
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
    $.when($.getJSON(url, function (result) {
        $("#verse").val(result);
    })).then(function () {
        getScan(poem, verse);
    });
}

function doScan(loc) {
    $.getJSON(loc, function (result) {
        if (result.includes('\n')) {
            result = result.replace('\n', '<br />');
        }
        $("#scannedVerse").html(result);
    });
}

function getScan(poem, verse) {
    doScan("/json/scan/" + poem + "/" + verse);
}

function getScanRaw(txt) {
    doScan("/json/scanraw/" + txt);
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
    $("#randomVerse").click(function () {
        var url = "/json/random/";
        $.getJSON(url, function (result) {
            // TODO: chain methods
            $("#author").val(result.author);
            getOpera(result.author, result.opus, result.book, result.poem);
            $("#verseNumber").val(result.number);
            $("#verse").val(result.verse);
        });
    });

    $("#author").change(function () {
        getOpera(this.value);
        getMaxVerseNumber($("#poem").val());
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

    $("#verse").focusout(function () {
        // getScan($("#poem").val(), $("#verseNumber").val());
        getScanRaw($("#verse").val());
    });

    $("#author").change();
    $("#opus").change();
    $("#book").change();

});
