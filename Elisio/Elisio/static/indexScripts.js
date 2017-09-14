var maxVerseNumber = 0;
var dict = true;
var avoidDouble = false;

function getOpera(key, op, bk, po) {
    var objects = $("#opusScannerField");
    objects.empty();
    $.when($.getJSON("/json/author/" + key, function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.full_name));
        });
        if (typeof op === "undefined")
            $('#opusScannerField option:first-child').attr("selected", "selected");
        else
            $("#opusScannerField").val(op);
    })).then(function () {
        getBooks($("#opusScannerField").val(), bk, po);
    });
}

function getBooks(key, bk, po) {
    var objects = $("#bookScannerField");
    objects.empty();
    $.when($.getJSON("/json/opus/" + key, function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.number));
        });
        if (typeof bk === "undefined")
            $('#bookScannerField option:first-child').attr("selected", "selected");
        else
            $("#bookScannerField").val(bk);
    })).then(function () {
        getPoems($("#bookScannerField").val(), po);
    });
}

function getPoems(key, po) {
    var objects = $("#poemScannerField");
    objects.empty();
    $.when($.getJSON("/json/book/" + key, function (result) {
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.number));
        });
        if (typeof po === "undefined")
            $('#poemScannerField option:first-child').attr("selected", "selected");
        else
            $("#poemScannerField").val(po);
    })).then(function () {
        getMaxVerseNumber($("#poemScannerField").val());
    });
}

function getMaxVerseNumber(key) {
    maxVerseNumber = 0;
    $.when($.getJSON("/json/poem/" + key, function (result) {
        maxVerseNumber = result;
    })).then(function () {
        $("#verseNumberScannerField").change();
    });
}

function getVerse(poem, verse) {
    var url = "/json/verse/" + poem + "/" + verse;
    $.when($.getJSON(url, function (result) {
        $("#verseContentsScannerField").val(result.verse.text);
        $("input[name=verseType][value='" + result.verse.type + "']").prop("checked", true);
    })).then(function () {
        getScan(poem, verse);
    });
}

function doScan(loc) {
    $.getJSON(loc, function (ret) {
        if (ret.text) {
            $("#scannedVerseResultField").html(ret.text);
            $("#zelenyResultField").html(ret.zeleny);
            $("#errorResultField").empty();
        }
        else {
            $("#scannedVerseResultField").empty();
            $("#zelenyResultField").empty();
            $("#errorResultField").html(ret.error.replace('\n', '<br />'));
        }
    });
}

function getScan(poem, verse) {
    doScan(useDict("/json/scan/dbverse/" + poem + "/" + verse));
}

function getScanRaw(txt) {
    doScan(useDict("/json/scan/text/" + txt));
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
    var regex = /^[0-9]+$/;
    if (!regex.test(val)) {
        $("#warningScannerField").text("Insert a number please");
    } else {
        $("#warningScannerField").empty();
    }
    if (val > maxVerseNumber) {
        $("#warningScannerField").text("Maximum verse number is " + maxVerseNumber);
    }
    return $("#warningScannerField").text() == "";
}

$(document).ready(function () {

    $("#randomVerseScannerButton").click(function () {
        avoidDouble = false;
        var url = "/json/verse/random/";
        $.getJSON(url, function (result) {
            $("#authorScannerField").val(result.author.id);
            $("#verseNumberScannerField").val(result.verse.number);
            $("#verseContentsScannerField").val(result.verse.text);
            $("input[name=verseType][value='"+ result.verse.type +"']").prop("checked", true);
            getOpera(result.author.id, result.opus.id, result.book.id, result.poem.id);
        });
    });

    $("#authorScannerField").change(function () {
        getOpera(this.value);
    });

    $("#opusScannerField").change(function () {
        getBooks(this.value);
    });

    $("#bookScannerField").change(function () {
        getPoems(this.value);
    });

    $("#poemScannerField").change(function () {
        getMaxVerseNumber(this.value);
    });

    $("#verseNumberScannerField").change(function () {
        var validated = validateVerseNumber(this.value);
        if (validated) {
            getVerse($("#poemScannerField").val(), this.value);
        }
        avoidDouble = true;
    });

    $("#verseContentsScannerField").focusout(function () {
        if (!avoidDouble)
            getScanRaw($("#verseContentsScannerField").val());
        avoidDouble = false;
    });


    $.when($.getJSON("/json/authors/", function (result) {
        var objects = $("#authorScannerField");
        $.each(result, function () {
            objects.append($("<option />").val(this.pk).text(this.fields.short_name));
        });
    })).then(function () {
        $("#authorScannerField").change();
    });

    $("#useDictCheckbox").change(function () {
        dict = this.checked;
    });

});
