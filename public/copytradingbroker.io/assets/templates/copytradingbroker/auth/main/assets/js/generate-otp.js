$('#generate-otp').click(function () {
    var value = $(this).html().trim();
    if (value == 'Proceed') {
        $(this).html('Proceed');
        $('#login-otp').css('display', "flex");
        $('#mobile-num').css('display', "none");
    } else {
        $(this).html('proceed');
        $('#login-otp').css('display', "flex");
        $('#mobile-num').css('display', "none");
    }
})
