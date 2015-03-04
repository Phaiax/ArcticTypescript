/// <reference path="insanity.ts" />


var countdown_element: HTMLElement = document.getElementById('countdown_display');
var countdown_helper = new Insanity.CountdownToInsanity(countdown_element);

countdown_helper.start()

var stop_element: HTMLElement = document.getElementById('stop');
stop_element.onclick = function() { countdown_helper.stop(); }
