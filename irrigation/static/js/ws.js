var app = app || {};

jQuery(document).ready(function ($) {
    var ws = new WebSocket('ws://' + rabbitmq_host + ':' + rabbitmq_ws_port + '/ws');
    var client = Stomp.over(ws);

    //client.debug = function () {
        // empty function to stop the PING, PONG printing
        // alternatively, we can make this do something different if we wanted...
    //};

    var on_connect = function (x) {
        client.subscribe(rabbitmq_topic, on_message);
    };

    var on_error = function (e) {
        console.log('error', e);
    };

    function on_message(m) {
        console.log('message received');
        console.log(m);
        zone_json = JSON.parse(m.body);
        update_toggle_zone_button(zone_json);
    }

    client.connect(rabbitmq_username, rabbitmq_password, on_connect, on_error, '/');
});