jQuery(document).ready(function ($) {
    $(".btn-toggle-zone").on('click', function () {
        var button = $(this);
        button.prop("disabled", true);

        var csrfCookieName = getCookie('csrftoken');
        var zoneId = button.attr('data-zone-id');

        $.ajax({
            type: "POST",
            url: '/toggle_zone/',
            dataType: "json",
            data: JSON.stringify({
                zoneId: zoneId,
            }),
            contentType: "application/json",
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrfCookieName);
                }
            }
        }).done(function (response) {
            if (response.success) {
                if (response.zone_is_on) {
                    button.removeClass('btn--red');
                    button.addClass('btn--green');
                } else {
                    button.removeClass('btn--green');
                    button.addClass('btn--red');
                }
                button.text(response.current_state);
            }
        }).always(function () {
            button.prop("disabled", false);
            button.find('i').hide();
        });
    });
});