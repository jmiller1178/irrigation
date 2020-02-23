jQuery(document).ready(function ($) {

    var currentTime = new Date().toLocaleTimeString();

    $('.timepicker').timepicker({
            step: 5,
            minTime: currentTime,
            maxTime: '11:00pm'
    });
    $('.timepicker').timepicker('option', { useSelect: true });
    $('.timepicker').timepicker('setTime', currentTime);
    $('.timepicker').timepicker({ 'timeFormat': 'h:i A' });
    $('.timepicker').timepicker({ 'forceRoundTime': true });
    $('.timepicker').timepicker({ 'disableTextInput': true});
    
    var dropdown = $('.schedule-dropdown');

    dropdown.empty();

    dropdown.append('<option selected="true" disabled>Choose Schedule</option>');
    dropdown.prop('selectedIndex', 0);

    schedules.forEach(function(schedule) {
        dropdown.append($('<option></option>').attr('value', schedule.scheduleId).text(schedule.displayName));
    });

    $(".schedule-dropdown").change(function(){
        var schedule = $(this);
        var time = $(".timepicker");
        var scheduleId = schedule.val();
        var startTime = time.val();
        get_schedule(scheduleId, startTime);
    });

    $('input.timepicker').on('changeTime', function() {
        var startTime = $(this).val();
        var schedule = $(".schedule-dropdown");
        var scheduleId = schedule.val();
        get_schedule(scheduleId, startTime);
    });
});

function get_schedule(scheduleId, startTime) {
    if (scheduleId && startTime) {
        var url = '/get_schedule/' + scheduleId + '/' + startTime;
        $.ajax({
            type: "GET",
            url: url,
        }).done(function (response) {
            console.debug(response);
        }).always(function () {
        
        });
    }
}