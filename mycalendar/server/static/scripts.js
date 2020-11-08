function del() {
    let title = document.getElementById("event-title");
    if (title.innerHTML == "") {
        title.removeAttribute("required");
    }
}

$("#getShareLink").click(function() {
    data = $.getJSON("/share/get-link",
    {
        "expiration": $("#expiration").val(),
        "share-content": $("#shareContent")[0].checked
    },
    function( data ) {
        $("#token").val(data["token"]);
    });
});

$("#token").focus(function() { 
    $(this).select();
    document.execCommand("copy");
    $('.alert').fadeIn(500).delay(2000).fadeOut(500)
});

if ($("#businesshour").length) {
    $("#businesshour").ready(function() {
        if ($("#businesshour")[0].checked) {
            $('#guestname').show();
        } else {
            $('#guestname').hide();
        }
    })
}

$("#businesshour").change(function() {
    if (this.checked) {
        $('#guestname').show();
    } else {
        $('#guestname').hide();
    }
});
