hs.tree = {};

hs.tree.Node = Ext.extend (Ext.tree.TreeNode, {
    constructor: function (field_type, config) {
	var fields = hs.data.fields[field_type].fields;
	
	this.getValue = function () {
	    var val = {};
	    for (key in fields) {
		val[key] = this[key];
	    }	    
	    return val;
	};

	for (key in fields) {
	    if ('title' in fields[key])
		config.text = config[key];
	}
	for (key in fields) {
	    this[key] = config[key];
	}

	Ext.apply (config, {
	    leaf: true,
	});
	hs.tree.Node.superclass.constructor.call (this, config);
    },
});

hs.tree.Panel = Ext.extend (Ext.tree.TreePanel, {
    constructor: function (data, config, node_config) {
	var thisPanel = this;
	if (!config)
	    config = {};
	if (!node_config)
	    node_config = {};
	var this_panel = this;
	var field_type = config.datatype;
	var fields = hs.data.fields[field_type].fields;
	var title_key = null;

	var root = new Ext.tree.TreeNode({
	    expanded: true,
	    expandable: true,
	});

	for (key in fields) {
	    if ('title' in fields[key])
		title_key = key;
	}

	var save = function (item) {
	    Ext.Ajax.request ({
		method: 'POST',
		url: '/' + hs.application + '/data/save/' + field_type,
		params: {
		    id: item.id,
		},
	    });
	    thisPanel.addChild (item);
	};

	this.addChild = function (item) {
	    var new_config = Ext.apply ({}, node_config);
	    Ext.apply (new_config, item);
	    root.appendChild (new hs.tree.Node (field_type, new_config));
	};

	for (var i = 0; i < data.length; i ++) {
	    var item = data[i];
	    this.addChild (item);
	}

	var buttons;
	if ('toolbar_buttons' in config) 
	    buttons = config.toolbar_buttons;
	else
	    buttons = [];
	buttons.push (new Ext.Button ({
	    icon: hs.extjs + '/icons/delete.gif',
	    handler: function (b) {
		var node = this_panel.getSelectionModel ().getSelectedNode ();
		Ext.Ajax.request ({
		    method: 'GET',
		    url: '/' + hs.application + '/data/unlink/' + field_type,
		    params: {
			id: node.id,
		    }
		});
		node.remove ();
	    },
	}));

	var new_config = {
	    title: hs.data.fields[field_type].text,
	    enableDD: true,
	    ddGroup: field_type,
	    root: root,
	    expanded: true,
	    collapsible: true,
	    listeners: {},
	    tbar: new Ext.Toolbar ({
		items: buttons,
	    }),
	};
	Ext.apply (new_config, config);
	new_config.listeners.beforenodedrop = function (dropEvent) {
	    var item = null;
	    if ('selections' in dropEvent.data)
		item = dropEvent.data.selections[0].data;
	    else if ('node' in dropEvent.data)
		item = dropEvent.dropNode;
	    if (dropEvent.source.tree == dropEvent.target.ownerTree)
		return false;
	    for (var i = 0; i < root.childNodes.length; i ++) {
		if (root.childNodes[i].id == item.id) {
		    return false;
		}
	    }
	    save (item);
	    return false;
	};
	hs.tree.Panel.superclass.constructor.call (this, new_config);
    },
});