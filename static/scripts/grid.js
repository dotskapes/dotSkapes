hs.grid = {};

hs.grid.getFields = function (name) {
    var fields = hs.data.fields[name].fields;
    var columnList = [];
    //for (var i = 0; i < fields.length; i ++) {
    for (key in fields) {
	columnList.push (key);
    }
    return columnList;
};

hs.grid.model = function (name) {
    var fields = hs.data.fields[name].fields;
    var columnList = [];
    //for (var i = 0; i < fields.length; i ++) {
    for (key in fields) {
	if (fields[key].visible == false)
	    continue;
	var val = {
	    header: fields[key].text,
	    dataIndex: key,
	    //id: name + '_' + key.name,
	    //width: 100,
	};
	if (fields[key].title)
	    columnList.unshift (val);
	else
	    columnList.push (val);
    }
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

	    if ('load_public' in config) {	    
		store = new Ext.data.JsonStore ({
		    root: 'data',
		    autoLoad: true,
		    fields: hs.grid.getFields (current_name),
		    url: '/' + hs.application + '/data/load/' + current_name + '/' + keyword + '?recommend=' + recommend,
		});
	    }
	};

	this.reload = function (name) {
	    thisPanel.getView ().dragZone.removeFromGroup (current_name);
	    if (name)
		current_name = name;
	    load ();
	    thisPanel.reconfigure (store, colModel);
	    thisPanel.getView ().dragZone.addToGroup (current_name);
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

	Ext.apply (config, {
	    colModel: colModel,
	    store: store,
	    enableDrag: true,
	    ddGroup: current_name,
	});

	hs.grid.Panel.superclass.constructor.call (this, config);
    },
});