module Insanity {
// it is allowed to split a single module across multiple files
// so it would be fine to have other files with module Insanity {}

	var start_time: number = 21;

	export class CountdownToInsanity{
		time_to_go: number;
		interval_id: number = null;
		insanity_intervall_id: number = null;
		bg_color_counter = 1;
		bg_colors: string[] = ['white', 'red', 'black', 'orange']


	    constructor(private element: HTMLElement){
	    }

	    public start(){
	    	this.time_to_go = start_time;
	        this.interval_id = setInterval(() => { this.tick() }, 1000)
	    }


	    private tick() {
	    	this.time_to_go -= 1;
	    	this.element.innerHTML = this.time_to_go.toString();
	    	if (this.time_to_go == 0) {
	    		this.stop();
	    		this.start_insanity();
	    	}
	    }

	    private start_insanity() {
	    	this.insanity_intervall_id = setInterval(() => {
	    			this.bg_color_counter = (this.bg_color_counter + 1) % this.bg_colors.length;
	    			document.body.style['background-color'] = this.bg_colors[this.bg_color_counter];
	    		}, 100);
	    }

	    public stop(){
	    	if (this.interval_id) {
	        	clearInterval(this.interval_id);
	    		this.interval_id = null;
	    	}
	    	if (this.insanity_intervall_id) {
	        	clearInterval(this.insanity_intervall_id);
	    		this.insanity_intervall_id = null;
	    	}
	    }

	}
}