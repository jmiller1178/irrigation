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
                // update_toggle_zone_button(response.zone)
            }
            else{
                var popup = $(".popup");
                var popup_close = $(".popup__close");
                popup_close.on('click', function(event){
                    popup.attr('style','visibility: hidden');
                    event.stopPropagation();
                    event.stopImmediatePropagation();
                    window.scrollTo(0,0);
                });
                
                var popup_text = $(".popup__text");
                // set the text of the popup
                popup_text.text(response.error);
                // show the text of the popup
                popup.attr('style','visibility: visible');
            }
        }).always(function () {
            button.prop("disabled", false);
            button.find('i').hide();
        });
    });

    $("[data-zone-id]").each(function(zone_button){
        var zone_id=$(this).attr('data-zone-id');
        var zone_data = findElement(zone_list, "zone_id", zone_id);
        console.debug(zone_id); 
        update_toggle_zone_button(zone_data);
        });
});

function update_toggle_zone_button(zone_data) {
    // first we have to find the right element
    // data-zone-id=zoneId
    var zone_button = $("[data-zone-id="+zone_data.zone_id+"]");
    if (zone_data.zone_is_on == "True"){
        zone_button.removeClass('btn--red');
        zone_button.addClass('btn--green');
    } else {
        zone_button.removeClass('btn--green');
        zone_button.addClass('btn--red');
    }
    zone_button.text(zone_data.current_state);
}