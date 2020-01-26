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
                update_toggle_zone_button(response.zone)
            }
        }).always(function () {
            button.prop("disabled", false);
            button.find('i').hide();
        });
    });
});

function update_toggle_zone_button(zone_data) {
    // first we have to find the right element
    // data-zone-id=zoneId
    var zone_button = $("[data-zone-id="+zone_data.zone_id+"]");
    if (zone_data.zone_is_on){
        zone_button.removeClass('btn--red');
        zone_button.addClass('btn--green');
    } else {
        zone_button.removeClass('btn--green');
        zone_button.addClass('btn--red');
    }
    zone_button.text(zone_data.current_state);
}