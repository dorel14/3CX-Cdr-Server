import { loadResource } from "../../static/utils/resources.js";

export default {
  template: "<div></div>",
  props: {
    options: Array,
    resource_path: String,
  },
  async mounted() {
    await this.$nextTick(); // NOTE: wait for window.path_prefix to be set
    await loadResource(window.path_prefix + `${this.resource_path}/index.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/locales-all.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/multimonth/index.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/daygrid/index.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/timegrid/index.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/list/index.global.min.js`);
    await loadResource(window.path_prefix + `${this.resource_path}/interaction/index.global.min.js`);
    this.options.eventClick = (info) => this.$emit("click", { info });
    //this.options.select = (info) => this.$emit("click", { info });
    this.options.dateClick = (info) => this.$emit("click", { info });
    this.calendar = new FullCalendar.Calendar(this.$el, this.options);
    this.calendar.render();
  },
  methods: {
    update_calendar() {
      if (this.calendar) {
        this.calendar.setOption("events", this.options.events);
        this.calendar.render();
      }
    },
  },
};