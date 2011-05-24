//var spatial_icon = '/' + hs.application + '/static/img/icon_spatial.png';

hs.side = {
    MapPanel: Ext.extend (hs.tree.Panel, {
	constructor: function (data, config) {
	    var mapPanel;
	    if (!config)
		config = {};

	    this.linkMap = function (map) {
		mapPanel = map;
	    };
	    
	    Ext.apply (config, {
		listeners: {
		    checkchange: function (node, checked) {
			if (checked) {
			    mapPanel.addMap (node);
			}
			else {
			    mapPanel.removeMap (node);
			}
		    },
		},
		datatype: 'maps',
	    });
	    
	    hs.side.MapPanel.superclass.constructor.call (this, data, config, {
		checked: false,
	    });
	},
    }),
    DevPanel: Ext.extend (hs.tree.Panel, {
	constructor: function (data, config) {
	    var thisPanel = this;
	    if (!config)
		config = {};
	    var createButton = new Ext.Button ({
		icon: '/' + hs.application + '/static/scripts/ext/examples/shared/icons/fam/add.png',
		handler: function (b) {
		    var win = new hs.win.dev.Create (thisPanel);
		    win.show ();
		},
	    });

	    var toolPanel;
	    this.setToolPanel = function (panel, tab, tn) {
		toolPanel = {
		    panel: panel,
		    tabPanel: tab,
		    toolnum: tn,
		};
	    };
	    Ext.apply (config, {
		toolbar_buttons: [
		    createButton,
		],
		datatype: 'dev_tools',
		title: 'Development Tools',
		enableDD: false,
		enableDrop: false,
		enableDrag: true,
		ddGroup: 'tools',
		listeners: {
		    dblclick: function (node) {
			var win = new hs.win.dev.Read (node, thisPanel, true, toolPanel, {
			    width: 700,
			    height: 500,
			});
			win.show ()
		    },
		},
	    });
	    hs.side.DevPanel.superclass.constructor.call (this, data, config);
	},
    }),
    ToolPanel: Ext.extend (hs.tree.Panel, {
	constructor: function (data, config) {
	    var thisPanel = this;
	    var toolPanel;

	    if (!config)
		config = {};

	    this.setToolPanel = function (panel, tab, tn) {
		toolPanel = {
		    panel: panel,
		    tabPanel: tab,
		    toolnum: tn,
		};
	    };
	    Ext.apply (config, {
		datatype: 'tools',
		listeners: {
		    dblclick: function (node) {
			var win = new hs.win.dev.Read (node, thisPanel, false, toolPanel, {
			    width: 700,
			    height: 500,
			});
			win.show ()
		    },
		},
	    });
	    hs.side.ToolPanel.superclass.constructor.call (this, data, config);
	},
    }),
    ResultPanel: Ext.extend (hs.tree.Panel, {
	constructor: function (data, config) {
	    if (!config)
		config = {};

	    Ext.apply (config, {
		datatype: 'results',
		listeners: {
		    dblclick: function (node, e) {
			var w = new hs.win.Result (node, config);
			w.show ();
		    },
		},
	    });
	    hs.side.ResultPanel.superclass.constructor.call (this, data, config);
	},
    }),
};