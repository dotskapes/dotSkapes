hs.grid = {
    fields: {
	{{ for key, val in data.iteritems (): }}
	{{= key }}: [
	    {{ for field in val: }}
	    {{ if not field.is_privilaged (): }}
	    {
		{{ if not field.display_settings.name: }}
		name: '{{= field.name () }}',
		{{ pass }}
		key: '{{= field.name () }}',
		{{ for k, v in field.display_settings.iteritems (): }}
		{{ if type (v) == bool: }}
		{{= k }}: {{= str(v).lower () }},
		{{ elif type (v) == str: }}
		{{= k }}: '{{= v }}',
		{{ elif type (v) == int or type (v) == float: }}
		{{= k }}: {{= v }},
		{{ pass }}
		{{ pass }}
	    },
	    {{ pass }}
	    {{ pass }}
	],
	{{pass}}
    },
};

hs.grid.getFields = function (name) {
    var fields = hs.grid.fields[name];
    var columnList = [];
    for (var i = 0; i < fields.length; i ++) {
	columnList.push (fields[i].key);
    }
    console.log (columnList);
    return columnList;
};

hs.grid.model = function (name) {
    var fields = hs.grid.fields[name];
    var columnList = [];
    for (var i = 0; i < fields.length; i ++) {
	var key = fields[i];
	var val = {
	    header: key.name,
	    dataIndex: key.key,
	    //id: name + '_' + key.name,
	    //width: 100,
	};
	if (key.title)
	    columnList.unshift (val);
	else
	    columnList.push (val);
    }
    console.log (columnList);
    return new Ext.grid.ColumnModel ({
	columns: columnList,
    });
};

hs.grid.Panel = Ext.extend (Ext.grid.GridPanel, {
    constructor: function (config) {
	var thisPanel = this;
	var colModel, store;

	var current_name = config.datatype;
	var keyword = '';
	var recommend = false;

	var load = function () {
	    colModel = hs.grid.model (current_name);

	    if (config.load_public) {	    
		store = new Ext.data.JsonStore ({
		    root: 'data',
		    autoLoad: true,
		    fields: hs.grid.getFields (current_name),
		    url: '/' + hs.application + '/data/load/' + current_name + '/' + keyword + '?recommend=' + recommend,
		});
	    }
	};

	this.reload = function (name) {
	    if (name)
		current_name = name;
	    load ();
	    thisPanel.reconfigure (store, colModel);
	};

	this.keyword = function (kw) {
	    keyword = kw;
	    load ();
	    thisPanel.reconfigure (store, colModel);
	};
	
	this.recommend = function (rec) {
	    recommend = rec;
	};

	load ();
	config.colModel = colModel
	config.store = store;

	hs.grid.Panel.superclass.constructor.call (this, config);
    },
});