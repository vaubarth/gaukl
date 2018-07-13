const utilsMixin = {
    data: {
        toggles: {
            logView: false,
            selectFolder: false,
            createProject: false,
            viewFlat: true,
            loading: false,
            start: false,
        },
        notifications: [],
        logs: [],
    },
    methods: {
        log: function (type, message) {
            let log = {type: {success: false, error: false, info: false, warning: false}, message: message, time: new Date().toISOString()};
            log.type[type] = true;
            this.logs.push(log)
        },
        notify: function (state, text) {
            that = this;
            let notification = {
                state: {success: false, error: false, info: false},
                text: text
            };
            notification.state[state] = true;
            this.notifications.push(notification);
            this.log(state, text);
            setTimeout(function () {
                that.notifications.shift();
            }, 10000);
        },
        toggle: function (toToggle) {
            this.toggles[toToggle] = !this.toggles[toToggle];
        }
    }
};