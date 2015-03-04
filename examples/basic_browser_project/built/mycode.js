var Insanity;
(function (Insanity) {
    // it is allowed to split a single module across multiple files
    // so it would be fine to have other files with module Insanity {}
    var start_time = 21;
    var CountdownToInsanity = (function () {
        function CountdownToInsanity(element) {
            this.element = element;
            this.interval_id = null;
            this.insanity_intervall_id = null;
            this.bg_color_counter = 1;
            this.bg_colors = ['white', 'red', 'black', 'orange'];
        }
        CountdownToInsanity.prototype.start = function () {
            var _this = this;
            this.time_to_go = start_time;
            this.interval_id = setInterval(function () { _this.tick(); }, 1000);
        };
        CountdownToInsanity.prototype.tick = function () {
            this.time_to_go -= 1;
            this.element.innerHTML = this.time_to_go.toString();
            if (this.time_to_go == 0) {
                this.stop();
                this.start_insanity();
            }
        };
        CountdownToInsanity.prototype.start_insanity = function () {
            var _this = this;
            this.insanity_intervall_id = setInterval(function () {
                _this.bg_color_counter = (_this.bg_color_counter + 1) % _this.bg_colors.length;
                document.body.style['background-color'] = _this.bg_colors[_this.bg_color_counter];
            }, 100);
        };
        CountdownToInsanity.prototype.stop = function () {
            if (this.interval_id) {
                clearInterval(this.interval_id);
                this.interval_id = null;
            }
            if (this.insanity_intervall_id) {
                clearInterval(this.insanity_intervall_id);
                this.insanity_intervall_id = null;
            }
        };
        return CountdownToInsanity;
    })();
    Insanity.CountdownToInsanity = CountdownToInsanity;
})(Insanity || (Insanity = {}));
/// <reference path="insanity.ts" />
var countdown_element = document.getElementById('countdown_display');
var countdown_helper = new Insanity.CountdownToInsanity(countdown_element);
countdown_helper.start();
var stop_element = document.getElementById('stop');
stop_element.onclick = function () { countdown_helper.stop(); };
// this is another source file
// there are no references to this file from other files mentioned in tsconfig.json[files]
// -> so this file has to be mentioned in tsconfig.json[files] to be compiled
// in contrast: insanity.ts is compiled automatically, because it is referenced in main.ts
// but it would be no harm, if insanity.ts would also be mentioned in tsconfig.json
window.main_two_has_been_executed = true;
//# sourceMappingURL=mycode.js.map