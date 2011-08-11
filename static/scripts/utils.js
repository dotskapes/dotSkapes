hs.util = {
    counter: 0,
    IFramePanel: Ext.extend (Ext.Panel, {
	constructor: function (config, src) {
	    var thisPanel = this;
	    var width = 0;
	    var height = 0;
	    var refresh = true;
	    var id = 'iframe' + hs.util.counter;
	    hs.util.counter ++;	 

	    if (!src)
		src = '';

	    var frame = document.createElement ('iframe');
	    frame.id = id;
	    frame.width = width;
	    frame.height = height;
	    frame.setAttribute ('frameborder', '0');
	    frame.setAttribute ('marginwidth', '0');
	    frame.setAttribute ('marginheight', '0');
	    frame.src = src;

	    this.src = function (s) {
		frame.src = s;
	    }

	    var resizeFrame = function () {
		console.log (thisPanel.body);
		var cWidth = thisPanel.body.getWidth () - 5;
		var cHeight = thisPanel.body.getHeight () - 5;
                p = thisPanel.body;
		f = frame;
		frame.width = cWidth;
		frame.height = cHeight;
	    }

	    Ext.apply (config, {
		listeners: {
		    afterrender: function (event) {
			this.body.appendChild (frame);
		    },
		    afterlayout: function (event) {
			resizeFrame ();
		    },
		    resize: function (event) {
			resizeFrame ();
		    },
		},
	    });
	    hs.util.IFramePanel.superclass.constructor.call (this, config);
	},
    }),
    SidePanel: Ext.extend (Ext.tree.TreePanel, {
	constructor: function (data, NodeType, node_config, config) {
	    if (!config)
		config = {};


	    var root = new Ext.tree.TreeNode({
		expanded: true,
	    });

	    for (var i = 0; i < data.length; i ++) {
		var item = data[i];
		//Ext.apply (node_config, item);
		var new_config = Ext.apply ({}, node_config);
		Ext.apply (new_config, item);
		root.appendChild (new NodeType (new_config));
	    }

	    Ext.apply (config, {
		//rootVisible: false,
		root: root,
		expanded: true,
		collapsible: true,
		/*enableDrag: true,
		dragConfig: {
		    ddGroup: 'tool',
		    dragAllowed: true,
		    dropAllowed: false,
		},*/
	    });
	    
	    hs.util.SidePanel.superclass.constructor.call (this, config);
	},
    }),
    Node: Ext.extend (Ext.tree.TreeNode, {
	keys: [],
	textField: '',
	constructor: function (config) {
	    for (var i = 0; i < this.keys.length; i ++) {
		var k = this.keys[i];
		this[k] = config[k];
	    }
	    config.text = config[this.textField];
	    hs.util.Node.superclass.constructor.call (this, config);
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
    extend: function (extElement, func) {
	return Ext.extend (extElement, {
	    constructor: func,
	});
    },
    dropTarget: function (extElement, htmlElement, config) {
	/*config.notifyDrop = (function (notify) {
	    return function (source, event, data) {
		console.log (data);
		return notify.call (extElement, source, event, data);
	    };
	}) (config.notifyDrop);*/
	return new Ext.dd.DropTarget (htmlElement, config);
    },
};