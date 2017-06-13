var maxVerseNumber = 0;
var dict = true;
var avoidDouble = false;

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
    $.when($.getJSON("/json/poem/" + key, function (result) {
        maxVerseNumber = result;
    })).then(function () {
        $("#verseNumber").change();
    });
}

function getVerse(poem, verse) {
    var url = "/json/verse/" + poem + "/" + verse;
    $.when($.getJSON(url, function (result) {
        $("#verse").val(result.verse.text);
        $("input[name=verseType][value='" + result.verse.type + "']").prop("checked", true);
    })).then(function () {
        getScan(poem, verse);
    });
}

function doScan(loc) {
    $.getJSON(loc, function (ret) {
        if (ret.text) {
            result = ret.text;
            $("#scannedVerse").html(ret.text);
            $("#zeleny").html(ret.zeleny);
            $("#error").empty();
        }
        else {
            $("#scannedVerse").empty();
            $("#zeleny").empty();
            $("#error").html(ret.error.replace('\n', '<br />'));
        }
    });
}

function getScan(poem, verse) {
    doScan(useDict("/json/scan/" + poem + "/" + verse));
}

function getScanRaw(txt) {
    doScan(useDict("/json/scanraw/" + txt));
}

function useDict(url) {
    var type = $('input[name="verseType"]:checked').val();
    if (!type) {
        type = 'UNKNOWN';
    }
    url += "?type=" + type;
    if (dict === false) {
        url += "&disableDict=true";
    }
    return url;
}

function validateVerseNumber(val) {
    var regex = /^[0-9]*$/;
    if (!regex.test(val)) {
        $("#warning").text("Insert a number please");
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
        avoidDouble = false;
        var url = "/json/random/";
        $.getJSON(url, function (result) {
            $("#author").val(result.author.id);
            $("#verseNumber").val(result.verse.number);
            $("#verse").val(result.verse.text);
            $("input[name=verseType][value='"+ result.verse.type +"']").prop("checked", true);
            getOpera(result.author.id, result.opus.id, result.book.id, result.poem.id);
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
        avoidDouble = true;
    });

    $("#verse").focusout(function () {
        // getScan($("#poem").val(), $("#verseNumber").val());
        if (!avoidDouble)
            getScanRaw($("#verse").val());
        avoidDouble = false;
    });

    $("#author").change();
    $("#opus").change();
    $("#book").change();

    $("#dict").change(function () {
        dict = this.checked;
    });

});
