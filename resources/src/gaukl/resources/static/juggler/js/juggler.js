Vue.component('service-entry', {
    template: '<li>{{ service.name }} - Sent responses: {{ service.events.responses.count }}</li>',
    props: ['service']
});

var app = new Vue({
    el: '#app',
    data: {
        services: []
    },
    methods: {
        getServices: function () {
            this.$http.get('api/services').then(response => {
                this.getServicesData(response.body);
            });
        },
        getServicesData: function (services) {
            that = this;
            services.forEach(function (service) {
                that.$http.get('/api/events?event=in&services='+service).then(response => {
                    that.services.push({
                        'name': service,
                        'events': {
                            'responses': {
                                'count': response.body.response.count
                            }
                        }
                    })
                });
            })
        }
    }
});

app.getServices();