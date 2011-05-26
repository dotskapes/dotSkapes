hs.tool = {
    Panel: Ext.extend (Ext.Panel, {
	constructor: function (savedResults, savedAnalyses, config) {
	    var descPanel;
	    var paramPanel;
	    var bottomPanel;

	    var rightPanel;
	    var resultPanel;

	    var submitButton;
	    var saveAnalysisButton;
	    var saveButton;

	    var resultMask, paramMask;

	    var values = {};
	    var tool_ob;

	    var result_id;

	    this.paramReady = false;

	    var thisElement = this;

	    var fetchParams = function (toolid) {
		paramMask.show ();

		values = {};
		
		var toolField =  new Ext.form.Field ({
		    value: toolid,
		    name: 'tool',
		    hidden: true,
		});
		
		Ext.Ajax.request ({
		    method: 'GET',
		    url: '/' + hs.application + '/tool/tool/args',
		    success: showParams,
		    params: {'id': toolid},
		});
	    };

	    var showParams = function (data) {
		paramMask.hide ();

		var args = JSON.parse (data.responseText);
		
		for (var i = 0; i < args.length; i ++) {
		    var field;
		    var key = args[i][0];
		    var label = args[i][1];
		    var type = args[i][2];
		    if (type == 'text' || type == 'number') {
			field = new hs.tool.params.Text ({
			    fieldLabel: label,
			    name: key,
			    /*listeners: {
				specialkey: function (field, event) {
				    submitField (submitButton, event);
				},
			    },*/
			});
		    }
		    else if (type == 'poly_map' || type == 'point_map') {
			field = new hs.tool.params.Map ({
			    autoWidth: true,
			    fieldLabel: label,
			    name: key,
			});
		    }
		    else if (type == 'agg') {
			var depends = args[i][3];
			field = new hs.tool.params.Agg (label, values[depends]);
		    }
		    else if (type == 'attr') {
			var depends = args[i][3];
			field = new hs.tool.params.Attr (values[depends], {
			    fieldLabel: label,
			    name: key,
			    width: 160,
			});
		    }
		    else if (type == 'select') {
			var store = [];
			for (var j = 3; j < args[i].length; j ++) {
			    store.push (args[i][j]);
			}
			field = new hs.tool.params.ComboBox ({
			    fieldLabel: label,
		    name: key,
			    width: 160,
			    store: store,
			});
		    }
		    else {
			console.error ('Should Never See This');
		    }
		    values[key] = field;
		    paramPanel.add (field);
		}
		thisElement.paramReady = true;
		submitButton.enable ();
		saveAnalysisButton.enable ();
		paramPanel.add (submitButton);
		paramPanel.doLayout ();
	    };

	    var getValues = function () {
		var vals = {};
		for (key in values) {
		    vals[key] = values[key].getValue ();
		}
		return vals;
	    };

	    function showResult (data, options) {
		resultMask.hide ();
		var doc = data.responseText;
		var resp = JSON.parse (doc);
		result_id = resp['id'];
		var docOb;
		if ('err' in resp) {
		    docOb = {
			html: resp['err'],
		    };
		}
		else {
		    docOb =  {
			html: '<iframe style="margin: 0px; padding: 0px; border: none;" width="' + (resultPanel.getInnerWidth () - 25)  + '" height="' + (resultPanel.getInnerHeight () - 25)  + '" src="/' + hs.application + '/tool/result/load?id=' + result_id + '"></iframe>',
		    };
		}

		saveButton.enable ();
		//publicButton.enable ();

		resultPanel.removeAll ();
		resultPanel.add (docOb);
		resultPanel.doLayout ();
	    };
	    
	    submitButton = new Ext.Button ({
		text: 'Submit Tool',
		disabled: true,
		listeners: {
		    click: function () {
			resultMask.show ();
			var vals = getValues ();
			vals.id = tool_ob.id;

			Ext.Ajax.request ({
			    method: 'GET',
			    url: '/' + hs.application + '/tool/tool/run',
			    success: showResult,
			    failure: function (data) {
				console.log ('Bad Param');
			    },
			    params: vals,
			});
		    },
		},
	    });


	    saveAnalysisButton = new Ext.Button ({
		text: 'Save Analysis',
		disabled: true,
		listeners: {
		    click: function () {
			Ext.MessageBox.prompt ('Save', 'Filename', function (b, text) {
			    var vals = getValues ();
			    vals.id = tool_ob.id; //JSON.stringify (tool_ob.getValue ());
			    vals.name = text;
			    Ext.Ajax.request ({
				method: 'GET',
				url: '/' + hs.application + '/tool/analysis/save',
				success: function (data) {
				    var result = JSON.parse (data.responseText);
				    if (!('err' in result)) {
					savedAnalyses.addChild (result);
					/*vals = JSON.stringify (getValues ());
					savedAnalyses.addChild ({
					    name: text,
					    tool: JSON.stringify (tool_ob.getValue ()),
					    json: vals,
					});*/
					//savedAnalyses.appendChild (text, JSON.stringify (tool_ob.getValue ()), vals);
				    }
				    else
					Ext.MessageBox.alert ('Error', result['err']);
				},
				failure: function (data) {
				    console.log ('Bad Param');
				},
				params: vals,
			    });
			});
		    },
		},
	    });
	    
	    saveButton = new Ext.Button ({
		text: 'Save',
		disabled: true,
		handler: function (b, e) {
		    Ext.MessageBox.prompt ('Save', 'Filename', function (b, text) {
			Ext.Ajax.request ({
			    method: 'GET',
			    url: '/' + hs.application + '/tool/result/save',
			    success: function (data) {
				var result = JSON.parse (data.responseText);
				if (!('err' in result)) {
				    savedResults.addChild (result);
				    //savedResults.appendChild (text, result['id']);
				}
				else
				    Ext.MessageBox.alert ('Error', result['err']);
			    },
			    params: {
				id: result_id,
				name: text,
			    },
			});
		    });
		},
	    });

	    var perm = 1;

	    /*var publicButton = new Ext.Button ({
		text: 'Make Result Public',
		disabled: true,
		handler: function (b, e) {
		    Ext.Ajax.request ({
			method: 'GET',
			url: '/' + hs.application + '/tool/result_perm',
			params: {
			    id: result_id,
			    perm: perm,
			},
		    });
		    if (perm) {
			b.setText ('Make Result Private');
			perm = 0;
		    }
		    else {
			b.setText ('Make Result Public');
			perm = 1;
		    }
		},
	    })*/;

            this.setField = function (key, value) {
		values[key].setField (value);
	    };

            this.dropTool = function (ob) {
		console.log ('Tool', ob);
		submitButton.disable ();
		saveAnalysisButton.disable ();
		this.paramReady = false;
		var el = {
		    xtype: 'panel',
		    html: '<b>Tool: </b>' + ob.name + '<br /><b>Description: </b>' + ob.desc,
		};
		
		tool_ob = ob;
		descPanel.removeAll ();
		//paramPanel.removeAll ();
		for (key in values) {
		    paramPanel.remove (values[key]);
		};
		resultPanel.removeAll ();
		
		descPanel.add (el);
		
		descPanel.doLayout ();
		paramPanel.doLayout ();
		resultPanel.doLayout ()
		
		fetchParams (ob.id);
	    };

            var dropTool = this.dropTool;

	    descPanel = new Ext.Panel ({
		height: 100,
		title: "Select Tool",
		hideBorders: true,
		padding: '10',
		items: [
		    {
			xtype: 'panel',
			html: "<b>Step 1:</b> Select Analysis <br /><br />",
		    },
		],
		listeners: {
		    render: function () {
			this.dropTarget = new Ext.dd.DropTarget (this.body, {
			    ddGroup: 'tools',
			    notifyDrop: function (source, event, data) {
				var node = data.node;
				dropTool (node);
				/*dropTool ({
				    id: node.attributes.tool_id,
				    name: node.text,
				    desc: node.attributes.desc
				});*/ 
			    },
			});
		    },
		},
	    });

	    paramPanel = new Ext.form.FormPanel ({
		layout: 'form',
		anchor: '100% -100',
		title: "Set Parameters",
		padding: '10',
		autoScroll: true,
		//hideBorders: true,
		border: false,
		listeners: {
		    render: function () {
	    		paramMask = new Ext.LoadMask (this.getEl (), {
			    msg: 'Fetching Parameters',
			});
		    },
		},
		buttons: [
		    saveAnalysisButton,
		    submitButton,
		],
	    });

	    resultPanel = new Ext.Panel ({
		region: 'center',
		title: 'Tool Result',
		padding: '10',
		hideBorders: true,
		autoScroll: true,
		buttonAlign: 'right',
		bodyBorder: false,
		buttons: [
		    //publicButton,
		    saveButton,
		],
		listeners: {
		    render: function () {
			resultMask = new Ext.LoadMask (this.getEl (), {
			    msg: 'Fetching Results',
			});
		    },
		},
	    });
	    
	    leftPanel = new Ext.Panel ({
		region: 'west',
		layout: 'anchor',
		//hideBorders: true,
		width: 300,
		items: [
		    descPanel,
		    paramPanel,
		],
	    });

	    /*bottomPanel = new Ext.Panel ({
		region: 'south',
		buttonAlign: 'right',
		bodyBorder: false,
		buttons: [
		    saveButton,
		],
	    });

	    rightPanel = new Ext.Panel ({
		region: 'center',
		layout: 'border',
		items: [
		    resultPanel,
		    bottomPanel,
		],
	    });*/

	    if (!config)
		config = {};

	    Ext.apply (config, {
		title: 'Analyzer',
		layout: 'border',
		items: [
		    leftPanel,
		    resultPanel,
		],
	    });

	    hs.tool.Panel.superclass.constructor.call (this, config);
	},
    }),
    Agg: {
	Window: Ext.extend (Ext.Window, {
	    constructor: function (map_ob, config) {
		var method = 'mean'
		var groups = [];
		var thisWindow = this;
		var aggPanel;
		
		this.getValue = function () {
		    return aggPanel.json ();
		    /*return {
			method: method,
			data: groups,
		    };*/
		};

		this.setField = function (preset) {
		    aggPanel.dropGroups ();
		    for (var i = 0; i  < preset.length; i ++) {
			var p = preset[i];
			var g = aggPanel.addGroup ();
			g.setName (p.name);
			g.setDir (p.dir);
			g.setMethod (p.method);
			g.setOutput (p.output);
			g.setData (JSON.parse (p.data));
		    }
		}
		
		var store = new GeoExt.data.AttributeStore ({
		    url: hs.geoserver.describe (map_ob)
		});
		store.load ();
		
		var attr = new Ext.grid.GridPanel ({
		    store: store,
		    region: 'east',
		    width: 220,
		    columns: [
			{
			    id: 'name',
			    header: 'Field',
			    width: 100,
			},
			{
			    id: 'type',
			    header: 'Type',
			    width: 100,
			},
		    ],
		    enableDrag: true,
		    ddGroup: 'attribute',
		});
		
		aggPanel = new hs.tool.Agg.Panel ({
		    region: 'center',
		});
		
		var addButton = new Ext.Button ({
		    text: 'Add Group',
		    handler: function () {
			aggPanel.addGroup ();
		    },
		});
		
		var doneButton = new Ext.Button ({
		    text: 'Done',
		    handler: function () {
			thisWindow.hide ();
		    }
		});
		
		var buttonPanel = new Ext.Panel ({
		    region: 'south',
		    layout: 'hbox',
		    height: 30,
		    items: [
			addButton,
			doneButton,
		    ],
		});
		
		hs.tool.Agg.Window.superclass.constructor.call (this, {
		    title: 'Define Aggregation',
		    closeAction: 'hide',
		    width: 600,
		    height: 400,
		    layout: 'border',
		    items: [
			aggPanel,
			buttonPanel,
			attr,
		    ],
		});
	    },
	}),
	Group: Ext.extend (Ext.Panel, (function () {
	    var groupCount = 0;
	    return {
		constructor: function  (config) {
		    var elements = [];
		    var extElement = this;
		    var recalcHeight = true;
		    var minHeight = 30;

		    this.name = 'Group ' + groupCount;
		    groupCount ++;

		    this.json = function () {
			console.log (fieldType.getValue ());
			var ob = {
			    name: this.name,
			    output: output.getValue (),
			    data: JSON.stringify (elements),
			    method: fieldMethod.getValue (),
			    dir: fieldType.getValue ().inputValue,
			}
			return ob;
		    }

		    this.setName = function (name) {
			this.name = name;
			nameField.setValue (name);
		    };

		    this.setDir = function (dir) {
			fieldType.setValue (dir);
		    };

		    this.setMethod = function (m) {
			fieldMethod.setValue (m);
		    };

		    this.setOutput = function (o) {
			output.setValue (o);
		    };

		    this.setData = function (ob) {
			for (var i = 0; i < ob.length; i ++) {
			    addAttr (ob[i][1], ob[i][0]);
			}
		    }

		    var output = new Ext.form.Checkbox ({
			boxLabel: 'Output',
		    });

		    var nameField = new Ext.form.Field ({
			value: this.name,
		    });

		    var fieldNames = new Ext.Panel ({
			hideBorders: true,
			items: [],
		    });

		    var fieldType = new Ext.form.RadioGroup ({
			items: [
			    {
				boxLabel: 'Point',
				inputValue: 'intern',
				name: 'group' + groupCount,
			    },
			    {
				boxLabel: 'Polygon',
				inputValue: 'extern',
				name: 'group' + groupCount,
			    },
			],
		    });

		    var fieldMethod = new hs.tool.params.ComboBox ({
			store: [['MEAN', 'Mean'], ['SUM', 'Sum'], ['COUNT', 'Count'], ['MIN', 'min'], ['MAX', 'MAX']],
			emptyText: 'Aggregation Method',
		    });

		    var addAttr = function (attrName, source) {
			elements.push ([
			    source,
			    attrName,
			]);
			console.log ('Context: ', this);
			recalcHeight = true;
			refresh ();
		    };
		    
		    var refresh = function () {
			var markup = '<b>';
			for (var i = 0; i < elements.length; i ++) {
			    markup += elements[i][1] + '<br />';
			}
			markup += '</b>';
			fieldNames.removeAll ();
			fieldNames.add ({
			    html: markup,
			});
			extElement.setHeight ('auto');
			fieldNames.doLayout ();
		    };

		    var dropTarget;

		    var contains = function (el, source) {
			//Better to use a hash table. Linear searching OK for now
			for (var i = 0; i < elements.length; i ++) {
			    var pair = elements[i];
			    if (pair[0] == source && pair[1] == el)
				return true;
			}
			return false;
		    };
		    if (!config)
			config = {};
		    Ext.apply (config, {
			draggable: {
			    ddGroup: 'attribute',
			    startDrag: function (event) {
				dropTarget.lock ();
			    },
			    endDrag: function (event) {
				dropTarget.unlock ();
			    },
			},
			hideBorders: true,
			items: [
			    nameField,
			    output,
			    fieldType,
			    fieldMethod,
			    fieldNames,
			],
			listeners: {
			    render: function () {
				dropTarget = hs.util.dropTarget (this, this.body, {
				    ddGroup: 'attribute',
				    notifyDrop: function (source, event, data) {		    
					if ('selections' in data) {
					    console.log (data);
					    var items = data.selections;
					    for (var i = 0; i < items.length; i ++) {
						var name = items[i].data.name;
						if (!contains (name, 'Map')) {
						    addAttr (name, 'Map');
						}
					    }
					}
					else if ('panel' in data) {
					    var panel = data.panel;
					    if (!contains (panel.name, null))
						addAttr (panel.name, null);
					}
				    },
				});
			    },
			    afterlayout: function () {
				if (recalcHeight) {
				    console.log (this.getInnerHeight ())
				    
				    if (this.getInnerHeight () <= minHeight) {
					recalcHeight = false;
					this.setHeight (30);
					minHeight = this.getInnerHeight ();
				    }
				    else {
					recalcHeight = false;
					this.setHeight ('auto');
				    }
				}
			    },
			},
			enableDrag: true,
			ddGroup: 'attribute',
		    });
		    hs.tool.Agg.Group.superclass.constructor.call(this, config);
		},
	    };
	}) ()),
	Panel: Ext.extend (Ext.Panel, (function () {
	    return {
		constructor: function (config) {
		    var groupConfig = {};
		    var groups = [];
		    var group0 = new hs.tool.Agg.Group (groupConfig);

		    this.addGroup = function () {
			var nextGroup = new hs.tool.Agg.Group (groupConfig);
			groups.push (nextGroup);
			this.add (nextGroup);
			this.doLayout ();
			return nextGroup;
		    };
		    
		    this.dropGroups = function () {
			this.removeAll ();
			groups = [];
			this.doLayout ();
		    };
		    

		    this.json = function () {
			var obs = [];
			for (var i = 0; i < groups.length; i ++) {
			    obs.push (groups[i].json ());
			}
			return JSON.stringify (obs);
		    };
			
		    if (!config)
			config = {};
		    groups.push (group0);
		    Ext.apply (config, {
			title: 'Set Groups',
			autoScroll: true,
			items: [
			    group0,
			],
		    });
		    hs.tool.Agg.Panel.superclass.constructor.call (this, config);
		},
	    };
	}) ()),
    },
			      
    params: {
	Map: Ext.extend (Ext.form.Field, {
	    constructor: function (config) {
		var store;
		var map_ob = null;

		this.getAttr = function () {
		    var records = [];
		    for (var i = 0; i < store.getTotalCount (); i ++) {
			records.push (store.getAt (i));
		    }
		    return records;
		};

		var thisField = this;

		this.setField = function (map) {
		    try {
			map_ob = JSON.parse (map);
		    }
		    catch (err) {
			map_ob = map;
		    }
		    this.setValue (map_ob.name);
		    store = new GeoExt.data.AttributeStore ({
			url: hs.geoserver.describe (map_ob)
		    });
		    store.load ();
		};

		this.getValue = function () {
		    return JSON.stringify (map_ob);
		};
		
		if (!config)
		    config = {};
		Ext.apply (config, {
		    readOnly: true,
		    listeners: {
			render: function () {
			    this.dropZone = new Ext.dd.DropTarget (thisField.getEl (), {
				ddGroup:'maps',
				notifyDrop: function (source, event, data) {
				    var node = data.node;
				    thisField.setField (node.getValue ());
				    /*thisField.setField ({
					id: node.attributes.filename,
					name: node.text,
					type: node.attributes.type,
				    });*/
				},
			    });
			},
		    },
		});
		hs.tool.params.Map.superclass.constructor.call (this, config);
	    },
	}),
	ComboBox: Ext.extend (Ext.form.ComboBox, {
	    setField: function (name) {
		this.setValue (name);
	    },
	}),
	Text: Ext.extend (Ext.form.Field, {
	    setField: function (name) {
		this.setValue (name);
	    },
	}),
	Attr: Ext.extend (Ext.form.ComboBox, {
	    constructor: function (depends, config) {

		var mapname = '';

		var store = new Ext.data.ArrayStore ({
		    fields: [
			'name',
		    ],
		    data: [],
		});

		var thisField = this;

		this.setField = function (name) {
		    this.setValue (name);
		};

		if (!config)
		    config = {};
		Ext.apply (config, {
		    emptyText: 'Select an Attribute',
		    displayField: 'name',
		    valueField: 'name',
		    mode: 'local',
		    store: store,
		    listeners: {
			beforequery: function (event) {
			    var map = JSON.parse (depends.getValue ());
			    if (!map)
				return;
			    mapname = map.id;
			    store.removeAll ();
			    store.add (depends.getAttr ());
			    event.combo.lastQuery = null;
			},
		    },
		});
		hs.tool.params.Attr.superclass.constructor.call (this, config);
	    },
	}),
	Agg: Ext.extend (Ext.Button, {
	    constructor: function (label, mapSource, config) {
		var map;
		var w;

		this.getValue = function () {
		    //if (preset)
		        //return JSON.stringify (preset);
		    console.log ('val', w.getValue ());
		    if (w) {
			return JSON.stringify ({
			    map: map,
			    data: w.getValue (),
			});
		    }
		    else
			return '{}';
		};

		var thisValue = this;
		
		this.setField = function (ob) {
		    var preset = JSON.parse (ob);
		    map = preset.map;
		    data = JSON.parse (preset.data);
		    w = new hs.tool.Agg.Window (map);
		    w.setField (data);
		    w.show ();
		    w.hide ();
		};

		if (!config) config = {}
		Ext.apply (config, {
		    fieldLabel: label,
		    text: 'Configure',
		    handler: function (event) {
			map = JSON.parse (mapSource.getValue ());
			if (!map)
			    return;
			if (!w)
			    w = new hs.tool.Agg.Window (map);
			w.show ();
		    },
		});
		hs.tool.params.Agg.superclass.constructor.call(this, config);
	    },
	}),
    }
}