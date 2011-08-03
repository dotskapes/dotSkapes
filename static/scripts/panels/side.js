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

	    var buttons = [];
	    
	    if (hs.user.admin) {
		var syncButton = new Ext.Button ({
		    text: 'Sync Geoserver',
		    handler: function (b) {
			Ext.Ajax.request ({
			    method: 'GET',
			    url: hs.url ('geoserver', 'sources'),
			    success: function (data) {
				var sources = JSON.parse (data.responseText);

				var root = new Ext.tree.TreeNode ({});

				var sync_geoserver = function (path) {
				    Ext.Ajax.request ({
					method: 'GET',
					url: hs.url ('geoserver', 'sync'),
					params: {
					    path: path,
					},
					success: function (data) {
					    var resp = JSON.parse (data.responseText);
					    if ('err' in resp)
						console.log (resp.err);
					    if (resp.code == 1)
						root.appendChild ({
						    text: resp.path,
						    leaf: true,
						})
					    else
						console.log ('Ok');
					},
				    });				    
				};

				for (var i = 0; i < sources.length; i ++) {
				    root.appendChild ({
					text: sources[i],
					leaf: true,
					listeners: {
					    dblclick: function (node) {
						sync_geoserver (node.text);
					    },
					},
				    });
				}

				var input = new Ext.form.TextField ({
				    region: 'south',
				    height: 30,
				});

				var delete_button = new Ext.Button ({
				    text: 'Remove Geoserver',
				    handler: function (b) {
					var node = tree.getSelectionModel ().getSelectedNode ();
					if (!node)
					    return;
					Ext.Ajax.request ({
					    method: 'GET',
					    url: hs.url ('geoserver', 'desync'),
					    params: {
						path: node.text,
					    },
					    success: function (data) {
						var resp = JSON.parse (data.responseText);
						if ('err' in resp)
						    console.log (resp.err);
						else {
						    node.remove ();
						    console.log ('Ok');
						}
					    },
					});
				    },
				});

				var add_button = new Ext.Button ({
				    text: 'Add Geoserver',
				    handler: function (b) {
					sync_geoserver (input.getValue ());
				    },
				});
				
				var tree = new Ext.tree.TreePanel ({
				    region: 'center',
				    root: root,
				    rootVisible: false,
				});

				var win = new Ext.Window ({
				    title: 'Geoserver Sources',
				    width: 300,
				    height: 400,
				    layout: 'border',
				    items: [
					tree,
					input,
				    ],
				    buttons: [
					delete_button,
					add_button,
				    ],
				});
				win.show ();
			    }
			});
		    },
		});
		buttons.push (syncButton);
	    }
	    
	    Ext.apply (config, {
		toolbar_buttons: buttons,
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
		icon: '/' + hs.application + '/static/scripts/ext/icons/add.png',
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
    AnalysisPanel: Ext.extend (hs.tree.Panel, {
	constructor: function (data, config) {
	    if (!config)
		config = {};

	    var toolPanel;
	    var tabPanel;
	    var toolnum;

	    this.setToolPanel = function (panel, tab, tn) {
		toolPanel = panel;
		tabPanel = tab;
		toolnum = tn;
	    };

	    Ext.apply (config, {
		datatype: 'analyses',
		listeners: {
		    dblclick: function (node, e) {
			tabPanel.setActiveTab (toolnum);
			var data = JSON.parse (node.json);
			var addParams = function () {
			    if  (!toolPanel.paramReady) {
				setTimeout (addParams, 100);
				return;
			    }
			    for (key in data) {
				toolPanel.setField (key, data[key]);
			    }
			};
			toolPanel.dropTool (JSON.parse (node.tool));
			setTimeout (addParams, 25);
		    },
		},
	    });
	    hs.side.AnalysisPanel.superclass.constructor.call (this, data, config);
	},
    }),
};