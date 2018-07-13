const editorMixin = {
    data: {
        editors: {
            'editors': [],
            'active': null
        }
    },
    computed:{
        activeEditor: function () {
            if(!this.editors.active) {
                return {'type': null, 'name': null, 'id': null};
            }
            that = this;
            return this.editors.editors.find(edi => {return edi.id === that.editors.active});
        }
    },
    methods: {
        loadContent: function (editor) {
            that = this;
            this.$http.get(`/api/${editor.type}/${editor.name}`).then(response => {
                editor.instance.setValue(response.body.content);
            });
        },
        addEditor: function (elem, type) {
            if (!this.editors.editors.find(obj => { return obj.id === elem.id })) {
                let editor = {
                    'id': elem.id,
                    'name': elem.name,
                    'type': type,
                    'instance': null
                };
                this.editors.editors.push(editor);
                this.$nextTick(function () {
                    this.initializeEditor(editor);
                });
            }
            this.setActive(elem.id);
        },
        initializeEditor: function (editor) {
            that = this;
            let langTools = ace.require("ace/ext/language_tools");
            editor.instance = ace.edit(editor.id);

            document.getElementById(editor.id).style.width = '100%';
            document.getElementById(editor.id).style.height = '800px'; // TODO:Relative

            //instance.setTheme("ace/theme/tomorrow");
            editor.instance.setTheme("ace/theme/merbivore_soft");
            editor.instance.getSession().setMode("ace/mode/yaml");
            editor.instance.resize();

            langTools.setCompleters([langTools.snippetCompleter]);
            editor.instance.setOptions({
                enableBasicAutocompletion: true,
                enableSnippets: true,
                enableLiveAutocompletion: true
            });
            editor.instance.commands.addCommand({
                name: 'save',
                bindKey: {win: 'Ctrl-S', mac: 'Cmd-S'},
                exec: function (instance) {
                    that.saveContent(editor)
                }
            });
            this.loadContent(editor);
        },
        setActive: function (editorId) {
            this.editors.active = editorId;
            let editor = this.editors.editors.find(edi => {
                return edi.id === editorId
            });
            let snipUrl = {'recipe': '/api/snippets/general,workflow,transformation', 'ruleset': '/api/snippets/general,test,manipulation', 'response': '/api/snippets/responses'};
            // Load snippets
            this.$http.get(snipUrl[editor.type]).then(response => {
                let snippetManager = ace.require("ace/snippets").snippetManager;
                let m = snippetManager.files[editor.instance.session.$mode.$id];
                if (m.snippets) {
                    snippetManager.unregister(m.snippets);
                }
                m.snippets = snippetManager.parseSnippetFile(response.body.snippets, m.scope);
                snippetManager.register(m.snippets);
            });
        },
        saveContent: function(editor) {
            that = this;
            this.$http.post(`/api/${editor.type}/${editor.name}`, {
                'content': editor.instance.getValue()
            }).then( response => {
                that.notify('success', `Saved ${editor.type} ${editor.name}`)
            }, response => {
                that.notify('error', `Could not save ${editor.type} ${editor.name}`)
            });
        }
    }
};