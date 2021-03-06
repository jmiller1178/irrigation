var app = app || {};

jQuery(document).ready(function ($) {
    var ws = new WebSocket('ws://' + rabbitmq_host + ':' + rabbitmq_ws_port + '/ws');
    var client = Stomp.over(ws);

    client.debug = function () {
       // empty function to stop the PING, PONG printing
       // alternatively, we can make this do something different if we wanted...
    };

    var on_connect = function (x) {
        client.subscribe('/topic/zone', on_zone_message);
        client.subscribe('/topic/system', on_system_message);
        client.subscribe('/topic/weather', on_weather_message);
        client.subscribe('/topic/rpigpiorequest', on_rpi_gpio_request_message);
        client.subscribe('/topic/norpigpiorequests', on_remove_all_rpi_gpio_requests_message);
    };

    var on_error = function (e) {
        console.log('error', e);
    };

    function on_zone_message(m) {
        console.log('zone message received');
        console.log(m);
        zone_json = JSON.parse(m.body);
        update_toggle_zone_button(zone_json);
    }

    function on_system_message(m) {
        console.log('system message received');
        console.log(m);
        system_json = JSON.parse(m.body);
        update_system_mode_button(system_json);
    }

    function on_weather_message(m) {
        console.log('weather message received');
        console.log(m);
        weather_json = JSON.parse(m.body);
        update_current_weather_conditions(weather_json);
    }

    function on_rpi_gpio_request_message(m) {
        console.log('rpi gpio request message received');
        console.log(m)
        rpio_gpio_request_json = JSON.parse(m.body);
        update_rpi_gpio_request(rpio_gpio_request_json);
    }

    function on_remove_all_rpi_gpio_requests_message(m) {
        console.log('remove all rpi gpio requests message received');
        console.log(m);
        remove_all_rpi_gpio_requests();
    }

    client.connect(rabbitmq_username, rabbitmq_password, on_connect, on_error, '/');
});