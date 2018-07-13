const app = new Vue({
    el: '#app',
    delimiters: ["[[", "]]"],
    mixins: [utilsMixin, editorMixin],
    data: {
        config: {},
        recipes: {
            recipes: []
        },
        pathList: {
            parent: {path:''},
            path: {}
        },
        newProject: {
            name: 'new project',
            path: '.'
        },
    },
    methods: {
        getConfig: function(callback) {
            this.$http.get('/api/config').then(response => {
                if(!response.body.error) {
                    that.config = response.body;
                    if(callback) {
                        callback();
                    }
                }
            });
        },
        setConfig: function (path) {
            this.$http.post('/api/config', {path: path}).then(response => {
                that.recipes.recipes = [];
                that.config = {};
                that.editors = {'editors': [], 'active': null};
                that.getConfig();
                that.loadRecipes();
            }, response => {
                that.notify('error', `Could not read as gaukl config ${path}`)
            });
        },
        loadRecipes: function () {
            this.$http.get('/api/recipes').then(response => {
                response.body.recipes.forEach(function (recipe) {
                    that.loadRecipe(recipe)
                })
            });
        },
        loadRecipe: function (recipe) {
            this.$http.get(`/api/recipes/${recipe.name}`).then(response => {
                that.recipes.recipes.push({
                    'id': recipe.id,
                    'name': recipe.name,
                    'rulesets': response.body.rulesets,
                    'responses': response.body.responses
                });
            });
        },
        getPathList: function (path) {
            this.$http.get('/api/listfolder', {params: {path: path}}).then(response => {
                that.pathList = response.body;
            }, response => {
                that.notify('error', 'Could not open folder, maybe you do not have permissions?');
            });
        },
        createNewProject: function() {
            // TODO: select path via pathbrowser
            this.$http.post('/api/createproject', {path: this.newProject.path, name: this.newProject.name}).then(response => {
                that.setConfig(`${that.newProject.path}/${that.newProject.name}/config.yaml`);
            }, response => {
                that.notify('error', `Could not create new project at ${that.newProject.path}`)
            });
        },
        init: function () {
            this.getConfig(this.loadRecipes());
        }
    }
});

Vue.http.interceptors.push(function(request, next) {
    that = this;
    this.toggle('loading');
    next(function(response) {
        that.toggle('loading');
    });
});