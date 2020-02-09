jQuery(document).ready(function ($) {
    //
    // When page is loaded this code executes once
    // after that, we rely on RabbitMQ and WebStomp to 
    // provide data messages with updates for the UI
    //
    
    // insert the table rows for the Manual Section
    var zone_table = $(".zone-table tbody");
    zone_list.forEach(function(zone) { 
        if (zone.visible){
            var new_zone_row = "<tr><td><span>" + zone.shortName + "</span></td>";
            new_zone_row += "<td><span>" + zone.locationName + "</span></td>";
            new_zone_row += "<td><span class=\"btn btn-toggle-zone\" data-zone-id=" + zone.zoneId + "></span></td></tr>";
            zone_table.append(new_zone_row);
        }
    });

    // insert the table rows for the Automatic Section
    var requests_table = $(".requests-table tbody");
    todays_requests.forEach(function(request) {
        var new_request_row = "<tr>";
        new_request_row += "<td><span>" + request.rpiGpio.zone.shortName + "</span></td>";
        new_request_row += "<td><span>" + request.rpiGpio.zone.locationName + "</span></td>;"
        new_request_row += "<td><span>" + request.on_time + "</span></td>";
        new_request_row += "<td><span>" + request.off_time + "</span></td>";
        new_request_row += "<td><span>" + parseInt(request.duration) + "</span></td>";
        new_request_row += "<td><span>" + parseInt(request.remaining) + "</span></td>";
        new_request_row += "<td><span class=\"btn btn-toggle-zone\" data-zone-id=" + request.rpiGpio.zone.zoneId + "></span></td></tr>";
        new_request_row += "</tr>"
        requests_table.append(new_request_row);
    });

    // update the system mode (Manual / Automatic) to reflect current state
    update_system_mode_button(irrigation_system);

    // update the Manual Section zone toggle buttons
    $("[data-zone-id]").each(function(zone_button){
        var zone_id=$(this).attr('data-zone-id');
        var zone_data = findElement(zone_list, "zoneId", zone_id);
        console.debug(zone_id); 
        update_toggle_zone_button(zone_data);
        });

    // update the current weather conditions
    update_current_weather_conditions(current_weather_conditions);


    // Click handler for the system mode (Manual / Automatic) button
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
            
        }).always(function () {
            button.prop("disabled", false);
            button.find('i').hide();
        });
    });

    // click handler for any of the toggle zone buttons
    // including the System and Valves Enable buttons
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
                // couldn't toggle zone prorably because
                // the system is completely disabled
                var popup = $(".popup");
                var popup_close = $(".popup__close");
                popup_close.on('click', function(event){
                    popup.attr('style','visibility: hidden');
                    event.stopPropagation();
                    event.stopImmediatePropagation();
                    window.scrollTo(0,0);
                });
                // show the response error in the popup
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

// used to update the styles and text on zone toggle buttons
// including the System and Valves Enable buttons
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

// used to update the styles and text on the system mode button
function update_system_mode_button(system_data) {
    // this is the system mode (Manual / Automatic) button
    var system_mode_button = $(".btn-toggle-system-mode");
      
    // find the button for System Enable / Disable so 
    // we can assign it's zone ID
    var system_enabled_zone = $(".system-enabled-zone");
    system_enabled_zone.attr('data-zone-id', system_enabled_zone_data.zoneId);

    // find the button for Valves Enable / Disable so
    // we can assign it's zone ID
    var valves_enabled_zone = $(".valves-enabled-zone");
    valves_enabled_zone.attr('data-zone-id', valves_enabled_zone_data.zoneId);

    // set the text on the system mode (Manual / Automatic)
    var system_mode_name = system_data.system_mode['name'];
    system_mode_button.text(system_mode_name);

    var automatic_mode_section = $(".section-automatic-mode");
    var manual_mode_section = $(".section-manual-mode");

    // get the current system mode state short name (A or M)
    var system_mode_short_name = system_data.system_mode['short_name'];
    // if we're in Automatic mode we want to set the button
    // to GREEN and show the Automatic section + hide the Manual section
    if (system_mode_short_name == "A"){
        system_mode_button.removeClass('btn--white');
        system_mode_button.addClass('btn--green');
        automatic_mode_section.show();
        manual_mode_section.hide();
    } else {
        // if we're in Manual mode we want to set the button
        // to WHITE and show the Manual section + hide the Automatic section
        system_mode_button.removeClass('btn--green');
        system_mode_button.addClass('btn--white');
        automatic_mode_section.hide();
        manual_mode_section.show();
    }
}

// update the text for the current weather conditions
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

// update the rpio gpio request passed in
function update_rpi_gpio_request(rpi_gpio_request_json) {

}