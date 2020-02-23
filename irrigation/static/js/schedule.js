jQuery(document).ready(function ($) {

    var dropdown = $('.schedule-dropdown');

    dropdown.empty();

    dropdown.append('<option selected="true" disabled>Choose Schedule</option>');
    dropdown.prop('selectedIndex', 0);

    schedules.forEach(function(schedule) {
        dropdown.append($('<option></option>').attr('value', schedule.scheduleId).text(schedule.displayName));
    });

    $(".schedule-dropdown").change( function(){
        var schedule = $(this);
        
        var csrfCookieName = getCookie('csrftoken');
        var scheduleId = schedule.val();
        var url = '/get_schedule/' + scheduleId;
        $.ajax({
             type: "GET",
             url: url,
        //     contentType: "application/json",
        //     beforeSend: function (xhr, settings) {
        //         if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        //             xhr.setRequestHeader("X-CSRFToken", csrfCookieName);
        //         }
        //     }
        }).done(function (response) {
            console.debug(response);
        }).always(function () {
        //     schedule.prop("disabled", false);
        //     schedule.find('i').hide();
        });
    });
});