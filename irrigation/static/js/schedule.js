jQuery(document).ready(function ($) {

    var dropdown = $('.schedule-dropdown');

    dropdown.empty();

    dropdown.append('<option selected="true" disabled>Choose Schedule</option>');
    dropdown.prop('selectedIndex', 0);

    schedules.forEach(function(schedule) {
        dropdown.append($('<option></option>').attr('value', schedule.scheduleId).text(schedule.displayName));
    });
});