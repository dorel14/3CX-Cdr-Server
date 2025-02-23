import { loadResource } from "../../static/utils/resources.js";

export default {
  template: "<div></div>",
  props: {
    options: Array,
    resource_path: String,
  },
  async mounted() {
    await this.$nextTick(); // NOTE: wait for window.path_prefix to be set
    await loadResource('https://cdn.jsdelivr.net/npm/ical.js/build/ical.min.js');
    await loadResource('https://cdn.jsdelivr.net/npm/rrule@2.6.4/dist/es5/rrule.min.js');
    await loadResource(window.path_prefix + `${this.resource_path}/index.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/locales-all.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/multimonth/index.global.min.js`); 
    await loadResource(window.path_prefix + `${this.resource_path}/icalendar.index.global.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/rrule.index.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/daygrid/index.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/timegrid/index.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/list/index.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/interaction/index.global.min.js`);



    this.options.eventClick = (info) => this.$emit("eventClick", { info });
    //this.options.select = (info) => this.$emit("click", { info });
    this.options.dateClick = (info) => this.$emit("dateClick", { info });
    this.calendar = new FullCalendar.Calendar(this.$el,this.options,);
    this.calendar.refetchEvents()
    console.log("Calendar:", this.calendar);
    console.log("Calendar options:", this.options);
    console.log("Events source:", this.options.eventSources);
    console.log("Events:", this.options.events);
    this.calendar.render();
  },
  methods: {
    update_calendar() {
      if (this.calendar) {        
        this.calendar.setOption("events", this.options.events);
        console.log("Calendar options:", this.options);
        console.log(this.options.events);
        this.calendar.refetchEvents()
        this.calendar.render();
      }
    },
  },
};