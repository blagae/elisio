$(document).ready(function () {
    $("#syncFilesButton").click(function () {
        $.getJSON("/json/admin/sync/files", function () {
            alert("done syncing files");
        });
    });
    $("#syncDbButton").click(function () {
        $.getJSON("/json/admin/sync/db", function () {
            alert("done syncing db");
        });
    });

    $('#postMetadataForm').submit(function(e) {
        e.preventDefault();
        var input = $(this).serialize();
        input = JSON.stringify(input);
        $.ajax({
            url: "/json/admin/meta/",
            type: "POST",
            data: input,
            success: function () {
                alert("new item created, try again to add the texts !");
            }
        });
    });

    $.getJSON("/json/admin/users/", function (result) {
        $.each(result, function () {
            var content = "";
            content += "<tr>";
            content += "<td>" + this.fields.username + "</td>";
            content += "<td>" + this.fields.date_joined + "</td>";
            content += "<td>" + this.fields.last_login + "</td>";
            content += "<td>" + this.fields.is_superuser + "</td>";
            content += "<td>" + this.fields.is_active + "</td>";
            content += "</tr>";
            $("#usersTable").append(content);
        });
    })
});
