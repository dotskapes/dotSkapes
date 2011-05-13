hs.tree = {
    base: {
	/*Panel: Ext.extend (Ext.tree.TreePanel, {
	    constructor: function (datatype, name, NodeType, config) {
		var root = new Ext.tree.TreeNode({
		    expanded: true,
		    children: [],
		});
		
		var config = {};
		Ext.apply (config, {
		    title: name,
		    rootVisible: false,
		    root: root,
		    expanded: true,
		    collapsible: false,
		    enableDrag: true,
		    dragConfig: {
			ddGroup: datatype,
		    },
		    autoScroll: true,
		});
		
		var thisPanel = this;
		
		var addData = function (data) {
		    var result = JSON.parse (data.responseText);
		    for (var i = 0; i < result.length; i ++) {
			root.appendChild (new NodeType (result[i]));
		    }
		    thisPanel.doLayout ();
		};
		
		Ext.Ajax.request ({
		    method: 'GET',
		    url: '/' + hs.application + '/data/load/' + datatype,
		    success: addData,
		});
		
		hs.tree.base.Panel.superclass.constructor.call (this, config);
	    },
	}),*/
	Node: Ext.extend (Ext.tree.TreeNode, {
	    keys: [],
	    constructor: function (config) {
		var textField = '';
		for (var i = 0; i < this.keys.length; i ++) {
		    var k = this.keys[i];
		    console.log (k);
		    if (k.title)
			textField = k.name;
		    this[k] = config[k];
		}
		config.text = config[textField];
		hs.tree.base.Node.superclass.constructor.call (this, config);
	    },
	    getValue: function () {
		var dict = {};
		for (var i = 0; i < this.keys.length; i ++) {
		    var k = this.keys[i];
		    dict[k] = this[k];
		}
		return dict;
	    },
	}),
    },
};

hs.tree.nodes = {
    {{ for key, val in data.iteritems (): }}
    {{= key }}: Ext.extend (hs.tree.base.Node, {
	keys: [
	    {{ for field in val: }}
	    {{ if not field.is_privilaged (): }}
	    {
		name: '{{= field.name () }}',>
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
    }),
    {{ pass }}
};

/*hs.tree.panel = {
    {{ for key in data: }}
    {{= key }}: Ext.extend (hs.tree.base.Panel, {
	constructor: function (conifg) {
	    if (!config)
		config = {};
	    hs.tree.panel.{{=key}}.superclass.constructor.call (this, '{{ = key }}', '{{ = key.title ()}}', hs.tree.nodes.{{= key }}, config);
	},
    }),
    {{ pass }}
};*/

hs.tree.Panel = Ext.extend (Ext.tree.TreePanel, {
    constructor: function (config) {
	var NodeType = hs.tree.nodes[config.datatype];

	var root = new NodeType ({
	    expanded: true,
	    children: [],
	});
	
	Ext.apply (config, {
	    title: name,
	    rootVisible: false,
	    root: root,
	    expanded: true,
	    collapsible: false,
	    enableDrag: true,
	    dragConfig: {
		ddGroup: config.datatype,
	    },
	    autoScroll: true,
	});
	
	var thisPanel = this;
	
	var addData = function (data) {
	    data = JSON.parse (data.responseText);
	    for (var i = 0; i < data.length; i ++) {
		root.appendChild (new NodeType (data[i]));
	    }
	    thisPanel.doLayout ();
	};

	
	if (config.load_user) {
	    Ext.Ajax.request ({
		method: 'GET',
		url: '/' + hs.application + '/userdata/load/' + config.datatype,
		success: addData,
	    });
	}

	hs.tree.Panel.superclass.constructor.call (this, config);
    },
});