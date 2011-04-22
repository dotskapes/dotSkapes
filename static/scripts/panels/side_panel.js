//var spatial_icon = '/' + hs.application + '/static/img/icon_spatial.png';

hs.tree = {
    ToolNode: Ext.extend (hs.util.Node, {
	keys: ['id', 'name', 'desc'],
	textField: 'name',
    }),
    MapNode: Ext.extend (hs.util.Node, {
	keys: ['prefix', 'filename', 'name', 'type'],
	textField: 'name',
    }),
    ResultNode: Ext.extend (hs.util.Node, {
	keys: ['filename', 'lookup_id', 'public'],
	textField: 'filename',
    }),
    AnalysisNode: Ext.extend (hs.util.Node, {
	keys: ['filename', 'tool', 'data'],
	textField: 'filename',
    }),
    /*ToolNode: Ext.extend (Ext.tree.TreeNode, {
	constructor: function (config) {
	    this.id = config.id;
	    this.name = config.name;
	    this.desc = config.desc;
	    Ext.apply (config, {
		text: config.name,
		leaf: true,
	    });
	    hs.tree.ToolNode.superclass.constructor.call (this, config);
	},
	getValue: function () {
	    return {
		id: this.id,
		name: this.name,
		desc: this.desc,
	    };
	},
    }),*/
    /*MapNode: Ext.extend (Ext.tree.TreeNode, {
	constructor: function (config) {
	    this.filename = config.filename;
	    this.name = config.name;
	    this.type = config.type

	    Ext.apply (config, {
		text: config.name,
		leaf: true,
	    });

	    this.getValue = function () {
		return {
		    filename: this.filename,
		    name: this.name,
		    type: this.type,
		};
	    };
	    hs.tree.MapNode.superclass.constructor.call (this, config);
	},
    }),*/
    /*ResultNode: Ext.extend (Ext.tree.TreeNode, {
	constructor: function (config) {
	    this.filename = config.filename;
	    this.lookup_id = config.id;

	    Ext.apply (config, {
		text: config.filename,
		leaf: true,
	    });

	    this.getValue = function () {
		return {
		    filename: this.filename,
		    lookup_id: this.lookup_id,
		};
	    };
	    hs.tree.MapNode.superclass.constructor.call (this, config);
	},
    }),*/
};

hs.side = {
    ToolPanel: Ext.extend (hs.util.SidePanel, {
	constructor: function (data) {
	    var thisPanel = this;
	    var toolPanel;
	    this.setToolPanel = function (panel, tab, tn) {
		toolPanel = {
		    panel: panel,
		    tabPanel: tab,
		    toolnum: tn,
		};
	    };

	    this.appendChild = function (name, id, type) {
		console.log ("HERE");
		this.getRootNode ().appendChild (new hs.tree.ToolNode ({
		    name: name,
		    id: id,
		    type: type,
		}));
		thisPanel.doLayout ();
	    };

	    var devSide;
	    this.setDevSide = function (panel) {
		devSide = panel;
	    };

	    var config = {
		title: 'Tools',
		rootVisible: false,
		enableDrag: true,
		dragConfig: {
		    ddGroup: 'tool',
		    dragAllowed: true,
		    dropAllowed: false,
		},
		listeners: {
		    dblclick: function (node) {
			var toolWin = new hs.win.DevWin (node.id, thisPanel, devSide, node, false, toolPanel, {
			    width: 700,
			    height: 500
			});
			toolWin.show ();
		    },
		},
	    };
	    hs.side.ToolPanel.superclass.constructor.call (this, data, hs.tree.ToolNode, {
		leaf: true,
	    }, config);
	},
    }),
    DevPanel: Ext.extend (hs.util.SidePanel, {
	constructor: function (data) {
	    var thisPanel = this;

	    var toolPanel;
	    this.setToolPanel = function (panel, tab, tn) {
		toolPanel = {
		    panel: panel,
		    tabPanel: tab,
		    toolnum: tn,
		};
	    };

	    var toolSide;
	    this.setToolSide = function (panel) {
		toolSide = panel;
	    };

	    
	    this.appendChild = function (name, id, type) {
		this.getRootNode ().appendChild (new hs.tree.ToolNode ({
		    name: name,
		    id: id,
		    type: type,
		}));
		thisPanel.doLayout ();
	    };

	    var deleteButton = new Ext.Button ({
		text: 'Delete Dev Tool',
		handler: function (b) {
		    var root = thisPanel.getRootNode ();
		    for (var i = 0; i < root.childNodes.length; i ++) {
			var item = root.childNodes[i];
			if (item.isSelected ()) {
			    Ext.MessageBox.confirm ('Delete', 'Do you want to delete ' + item.name + '?', function (a) {
				if (a == 'yes') {
				    Ext.Ajax.request ({
					method: 'GET',
					url: '/' + hs.application + '/tool/dev_delete',
					success: function (data) {
					    Ext.MessageBox.alert ('Delete', item.name + ' has been deleted');
					    item.remove ();
					},
					params: {
					    id: item.id,
					},
				    });
				}
			    });
			}
		    }
		},
	    });
	    
	    var newToolButton = new Ext.Button ({
		text: 'Create New Tool',
		handler: function (b) {
		    
		    var toolTitle = new Ext.form.Field ({
			value: 'Tool Title',
			//columnWidth: .25,
		    });

		    var toolType = new Ext.form.RadioGroup ({
			//columnWidth: .25,
			items: [
			    {
				boxLabel: 'Python',
				inputValue: 'python',
				name: 'analysis_type',
			    },
			    {
				boxLabel: 'R',
				inputValue: 'r',
				name: 'analysis_type',
			    },
			],
		    });
		    
		    var w = new Ext.Window ({
			width: 200,
			items: [
			    toolTitle,
			    toolType,
			],
			buttons: [
			    new Ext.Button ({
				text: 'Cancel',
				handler: function (b) {
				    w.close ();
				},
			    }),
			    new Ext.Button ({
				text: 'Create Tool',
				handler: function (b) {
				    var createNewTool = function (data) {
					var resp = JSON.parse (data.responseText);
					if ('err' in resp) {
					    console.log (resp['err']);
					}
					else
					    thisPanel.appendChild (resp['name'], resp['id'], resp['type'])
				    };
				    
				    Ext.Ajax.request ({
					method: 'POST',
					url: '/' + hs.application + '/tool/create',
					success: createNewTool,
					params: {
					    name: toolTitle.getValue (),
					    type: toolType.getValue ().inputValue,
					},
				    });
				    w.close ();
				},
			    }),
			],
		    });
		    w.show ();
		},
	    });
	    var config = {
		title: 'Development Tools',
		border: false,
		rootVisible: false,
		enableDrag: true,
		dragConfig: {
		    ddGroup: 'tool',
		    dragAllowed: true,
		    dropAllowed: false,
		},
		listeners: {
		    dblclick: function (node) {
			var toolWin = new hs.win.DevWin (node.id, toolSide, thisPanel, node, true, toolPanel, {
			    width: 700,
			    height: 500
			});
			toolWin.show ();
		    },
		},
		buttons: [
		    deleteButton,
		    newToolButton,
		],
	    };

	    hs.side.DevPanel.superclass.constructor.call (this, data, hs.tree.ToolNode, {
		leaf: true,
	    }, config);

	},
    }),
    MapPanel: Ext.extend (hs.util.SidePanel, {
	constructor: function (data) {

	    var tree = this;

	    var mapPanel;
	    var layers = {};

	    this.linkMap = function (map) {
		mapPanel = map;
		console.log (mapPanel);
	    };

	    var save = function () {
		var mapList = [];
		var root = tree.root;
		for (var i = 0; i < root.childNodes.length; i ++) {
		    var item = root.childNodes[i];
		    mapList.push (item.getValue ());
		}
		Ext.Ajax.request ({
		    method: 'POST',
		    url: '/' + hs.application + '/geodata/save_maps',
		    params: {
			data: JSON.stringify (mapList),
		    },
		});
	    };

	    var config = {
		title: 'Maps',
		rootVisible: true,
		enableDD: true,
		dragConfig: {
		    ddGroup: 'layers',
		},
		dropConfig: {
		    ddGroup: 'layers',
		},
		listeners: {
		    beforenodedrop: function (dropEvent) {
			var root = tree.root;
			if (dropEvent.source.tree == dropEvent.target.ownerTree) {
			    //dropEvent.dropNode = new hs.tree.MapNode (dropEvent.dropNode.getValue ());
			    //console.log ("Removing:", dropEvent.source.tree.getRootNode ().removeChild (dropEvent.dropNode));
			    return true;
			}
			for (var i = 0; i < root.childNodes.length; i ++) {
			    if (root.childNodes[i].filename == dropEvent.dropNode.filename) {
				return false;
			    }
			}
			var new_config = dropEvent.dropNode.getValue ();
			new_config.checked = false;
			dropEvent.dropNode = new hs.tree.MapNode (new_config);
			return true;
		    },
		    nodedrop: function () {
			save ();
		    },
		    checkchange: function (node, checked) {
			console.log (node, checked);
			if (checked) {
			    mapPanel.addMap (node);
			}
			else {
			    mapPanel.removeMap (node);
			}
			    
			//var nodes = this.getRootNode ().childNodes;
			//for (var i = 0; i < nodes.length; i ++) {
			//    console.log (nodes[i]);
			//}
		    },
		},
	    };
	    hs.side.MapPanel.superclass.constructor.call (this, data, hs.tree.MapNode, {
		checked: false,
		leaf: true,
	    }, config);
	},
    }),
    /*Maps: Ext.extend (Ext.tree.TreePanel, {
	constructor: function (data, config) {
	    if (!config)
		config = {};

	    var childNode = function (filename, name, type) {
		return new Ext.tree.TreeNode ({
		    text: name,
		    leaf: true,
		    cls: 'file',
		    filename: filename,
		    type: type,
		});
	    };

	    var childNodes = [];
	    for (var i = 0; i < data.length; i ++) {
		var item = data[i];
		childNodes.push (childNode (item['filename'], item['name'], item['type']));
	    }

	    var root = new Ext.tree.AsyncTreeNode({
		text: 'Maps',
		expanded: true,
		children: childNodes,
	    });

	    var save = function () {
		var mapList = [];
		for (var i = 0; i < root.childNodes.length; i ++) {
		    var item = root.childNodes[i];
		    mapList.push ({
			filename: item.attributes.filename, 
			name: item.text, 
			type: item.attributes.type,
		    });
		}
		Ext.Ajax.request ({
		    method: 'POST',
		    url: '/' + hs.application + '/geodata/save_maps',
		    params: {
			data: JSON.stringify (mapList),
		    },
		});
	    };

	    Ext.apply (config, {
		title: 'Maps',
		rootVisible: true,
		root: root,
		expanded: true,
		collapsible: true,
		enableDD: true,
		dragConfig: {
		    ddGroup: 'layers',
		},
		dropConfig: {
		    ddGroup: 'layers',
		},
		listeners: {
		    beforenodedrop: function (dropEvent) {
			if (dropEvent.source.tree == dropEvent.target.ownerTree)
			    return true;
			for (var i = 0; i < root.childNodes.length; i ++) {
			    if (root.childNodes[i].attributes.filename == dropEvent.dropNode.attributes.filename) {
				return false;
			    }
			}
			dropEvent.dropNode =  new Ext.tree.AsyncTreeNode(dropEvent.dropNode.attributes);
			return true;
		    },
		    nodedrop: function () {
			save ();
		    },
		},
	    });

	    hs.side.Maps.superclass.constructor.call (this, config);
	},
    }),
    Tools: Ext.extend (Ext.tree.TreePanel, {
	constructor: function (data, config) {
	    if (!config)
		config = {};

	    var childNode = function (id, name, desc) {
		return {
		    text: name,
		    leaf: true,
		    cls: 'file',
		    tool_id: id,
		    desc: desc,
		};
	    };

	    var childNodes = [];
	    for (var i = 0; i < data.length; i ++) {
		var item = data[i];
		childNodes.push (childNode (item['id'], item['name'], item['desc']));
	    }

	    var root = new Ext.tree.AsyncTreeNode({
		expanded: true,
		children: childNodes,
	    });

	    Ext.apply (config, {
		title: 'Tools',
		rootVisible: false,
		root: root,
		expanded: true,
		collapsible: true,
		enableDrag: true,
		dragConfig: {
		    ddGroup: 'tool',
		    dragAllowed: true,
		    dropAllowed: false,
		},
	    });

	    hs.side.Tools.superclass.constructor.call (this, config);
	},
    }),*/
    ResultPanel: Ext.extend (hs.util.SidePanel, {
	constructor: function (data) {

	    this.appendChild = function (filename, lookup_id) {
		this.getRootNode ().appendChild (new hs.tree.ResultNode ({
		    filename: filename,
		    lookup_id: lookup_id,
		}));
		this.doLayout ();
	   };

	    var config = {};
	    Ext.apply (config, {
		title: 'Results',
		rootVisible: false,
		listeners: {
		    click: function (node, e) {
			var perm = node.public;
			var text = '';
			var urlPanel;

			function togglePerm  () {
			    if (perm) {
				text = 'Make Result Private';
				perm = 0;
			    }
			    else {
				text = 'Make Result Public';
				perm = 1;
			    }
			};
			togglePerm ();
			
			var result_id = node.lookup_id;
			var title = node.filename;

			var publicButton = new Ext.Button ({
			    text: text,
			    handler: function (b, e) {
				Ext.Ajax.request ({
				    method: 'GET',
				    url: '/' + hs.application + '/tool/result_perm',
				    params: {
					id: result_id,
					perm: perm,
				    },
				});
				togglePerm ();
				if (perm == 1)
				    urlPanel.hide ();
				else
				    urlPanel.show ();
				b.setText (text);
			    },
			});

			var w = new Ext.Window ({
			    width: 800,
			    height: 600,
			    title: title,
			    closeAction: 'close',
			    items: [],
			    buttons: [
				publicButton,
			    ],
			    listeners: {
				render: function (el) {
				    var panel = new Ext.Panel ({
					html: '<iframe style="margin: 0px; padding: 0px; border: none;" width="' + (775)  + '" height="' + (500)  + '" src="/' + hs.application + '/tool/get_result?id=' + result_id + '"></iframe>',

				    });

				    urlPanel = new Ext.Panel ({
					html: 'Public URL: http://zk.healthscapes.org/healthscapes/tool/get_result?id=' + result_id,
					hidden: (perm == 1),
				    });

				    this.add (panel);
				    this.add (urlPanel);
				    this.doLayout ();
				},
			    },
			});
			w.show ();
		    },
		},
	    });
	    
	    hs.side.ResultPanel.superclass.constructor.call (this, data, hs.tree.ResultNode, {
		leaf: true,
	    }, config);
	},
    }),
    AnalysisPanel: Ext.extend (hs.util.SidePanel, {
	constructor: function (data) {
	    var toolPanel;
	    var tabPanel;
	    var toolnum;

	    this.setToolPanel = function (panel, tab, tn) {
		toolPanel = panel;
		tabPanel = tab;
		toolnum = tn;
	    };

	    this.appendChild = function (filename, tool, data) {
		this.getRootNode ().appendChild (new hs.tree.AnalysisNode ({
		    filename: filename,
		    tool: tool,
		    data: data,
		}));
		this.doLayout ();
	   };

	    var config = {};
	    Ext.apply (config, {
		title: 'Saved Analyses',
		rootVisible: false,
		listeners: {
		    click: function (node) {
			tabPanel.setActiveTab (toolnum);
			var data = JSON.parse (node.data);
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

	    hs.side.ResultPanel.superclass.constructor.call (this, data, hs.tree.AnalysisNode, {
		leaf: true,
	    }, config);
	},
    }),
    /*SavedResults: Ext.extend (Ext.tree.TreePanel, {
	constructor: function (data, config) {

	    var childNode = function (filename, id) {
		return {
		    text: filename,
		    //icon: spatial_icon,
		    leaf: true,
		    cls: 'file',
		    lookup_id: id,
		};
	    };

	    var childNodes = [];
	    for (var i = 0; i < data.length; i ++) {
		var item = data[i];
		console.log (item['id']);
		childNodes.push (childNode (item['filename'], item['id']));
	    }
	    
	   
	    var root = new Ext.tree.AsyncTreeNode({
		expanded: true,
		children: childNodes,
	    });

	    this.appendChild = function (filename, id) {
		root.appendChild (childNode (filename, id));
		this.doLayout ();
	    };

	    if (!config)
		config = {};

	    Ext.apply (config, {
		rootVisible: false,
		root: root,
		listeners: {
		    click: function (node, e) {
			var result_id = node.attributes.lookup_id;
			var title = node.text;
			console.log (node);
			var w = new Ext.Window ({
			    width: 800,
			    height: 600,
			    title: title,
			    closeAction: 'close',
			    items: [],
			    listeners: {
				render: function (el) {
				    var panel = new Ext.Panel ({
					html: '<iframe style="margin: 0px; padding: 0px; border: none;" width="' + (775)  + '" height="' + (575)  + '" src="/' + hs.application + '/tool/get_result?id=' + result_id + '"></iframe>',
				    });
				    this.add (panel);
				    this.doLayout ();
				},
			    },
			});
			w.show ();
		    },
		},
	    });

	    hs.side.SavedResults.superclass.constructor.call (this, config);
	},
    }),
    SavedAnalyses: Ext.extend (Ext.tree.TreePanel, {
	constructor: function (data, config) {
	    var toolPanel;
	    var tabPanel;
	    var toolnum;

	    this.setToolPanel = function (panel, tab, tn) {
		toolPanel = panel;
		tabPanel = tab;
		toolnum = tn;
	    };

	    var childNode = function (filename, tool, data) {
		return {
		    text: filename,
		    //icon: spatial_icon,
		    leaf: true,
		    cls: 'file',
		    tool: tool,
		    data: data,
		};
	    };

	    var childNodes = [];


	    for (var i = 0; i < data.length; i ++) {
		var item = data[i];
		var steps = JSON.parse (item['data']);
		console.log (item['tool']);
		var tool =  JSON.parse (item['tool']);
		childNodes.push (childNode (item['filename'], tool, steps));
	    }	    
	   
	    var root = new Ext.tree.AsyncTreeNode({
		expanded: true,
		children: childNodes,
	    });

	    this.appendChild = function (filename, tool, data) {
		root.appendChild (childNode (filename, tool, data));
		this.doLayout ();
	    };

	    if (!config)
		config = {};

	    Ext.apply (config, {
		rootVisible: false,
		root: root,
		listeners: {
		    click: function (node) {
			tabPanel.setActiveTab (toolnum);
			var tool = node.attributes.tool_id;
			var data = node.attributes.data;
			var addParams = function () {
			    if  (!toolPanel.paramReady) {
				setTimeout (addParams, 100);
				return;
			    }
			    for (key in data) {
				console.log (key);
				toolPanel.setField (key, data[key]);
			    }
			};
			toolPanel.dropTool (node.attributes.tool);
			setTimeout (addParams, 25);
		    },
		},

	    });

	    hs.side.SavedAnalyses.superclass.constructor.call (this, config);    
	},
    }),*/
};