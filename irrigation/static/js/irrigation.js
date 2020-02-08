jQuery(document).ready(function ($) {
    var zone_table = $(".zone-table tbody");
    zone_list.forEach(function(zone) { 
        if (zone.visible){
            var new_zone_row = "<tr><td><span>" + zone.shortName + "</span></td>";
            new_zone_row += "<td><span>" + zone.locationName + "</span></td>";
            new_zone_row += "<td><span class=\"btn btn-toggle-zone\" data-zone-id=" + zone.zoneId + "></span></td></tr>";
            zone_table.append(new_zone_row);
        }
    });

    update_system_mode_button(irrigation_system);

    $("[data-zone-id]").each(function(zone_button){
        var zone_id=$(this).attr('data-zone-id');
        var zone_data = findElement(zone_list, "zoneId", zone_id);
        console.debug(zone_id); 
        update_toggle_zone_button(zone_data);
        });
    update_current_weather_conditions(current_weather_conditions);



    $(".btn-toggle-system-mode").on('click', function(){
        var button = $(this);
        button.prop("disabled", true);
        var csrfCookieName = getCookie('csrftoken');
        $.ajax({
            type: "POST",
            url: '/toggle_system_mode/',
            dataType: "json",
            contentType: "application/json",
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrfCookieName);
                }
            }
        }).done(function (response) {
            //update_system_mode_button(response);
        }).always(function () {
            button.prop("disabled", false);
            button.find('i').hide();
        });
    });

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
            if (!response.success) {
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

});

function update_toggle_zone_button(zone_data) {
    // first we have to find the right element
    // data-zone-id=zoneId
    var zone_button = $("[data-zone-id="+zone_data.zoneId+"]");
    if (zone_data.is_on == true){
        zone_button.removeClass('btn--red');
        zone_button.addClass('btn--green');
    } else {
        zone_button.removeClass('btn--green');
        zone_button.addClass('btn--red');
    }
    zone_button.text(zone_data.currentState);
}

function update_system_mode_button(system_data) {
    var system_mode_button = $(".btn-toggle-system-mode");
    var system_mode_name = system_data.system_mode['name'];
    var system_mode_short_name = system_data.system_mode['short_name'];
    var automatic_mode_section = $(".section-automatic-mode");
    var manual_mode_section = $(".section-manual-mode");

    var system_enabled_zone = $(".system-enabled-zone");
    system_enabled_zone.attr('data-zone-id', system_enabled_zone_data.zoneId);
    // system_enabled_zone.text(system_enabled_zone_data.currentState);
    var valves_enabled_zone = $(".valves-enabled-zone");
    valves_enabled_zone.attr('data-zone-id', valves_enabled_zone_data.zoneId);
    // valves_enabled_zone.text(valves_enabled_zone_data.currentState);

    system_mode_button.text(system_mode_name);

    if (system_mode_short_name == "A"){
        system_mode_button.removeClass('btn--white');
        system_mode_button.addClass('btn--green');
        automatic_mode_section.show();
        manual_mode_section.hide();
    } else {
        system_mode_button.removeClass('btn--green');
        system_mode_button.addClass('btn--white');
        automatic_mode_section.hide();
        manual_mode_section.show();
    }
}

function update_current_weather_conditions(weather_json) {
    var condition_date_time = $(".condition-date-time");
    var condition_code_description = $(".condition-code-description");
    var condition_temperature = $(".condition-temperature");
    var condition_temperature_uom = $(".condition-temperature-uom");
    var condition_raining = $(".condition-raining");

    var conditionDateTime=new Date(weather_json['conditionDateTime']);

    condition_code_description.text(weather_json['conditionCode'].description);
    condition_date_time.text(conditionDateTime.toLocaleString("en-US"));
    condition_temperature.text(parseInt (weather_json['temperature']));
    condition_temperature_uom.text(weather_json['unitOfMeasure']);
    condition_raining.text(weather_json['raining_message']);
}