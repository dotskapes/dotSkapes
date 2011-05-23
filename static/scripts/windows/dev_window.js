hs.win = {
    DevCreate: Ext.extend (Ext.Window, {
	constructor: function (thisPanel) {
	    var thisWin = this;
	    var config = {};

	    var toolTitle = new Ext.form.TextField ({
		emptyText: 'Tool Title',
		width: 300,
		//columnWidth: .25,
	    });
	    
	    var toolType = new Ext.form.RadioGroup ({
		//columnWidth: .25,
		width: 300,
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
	    
	    var toolDesc = new Ext.form.TextArea ({
		width: 300,		
		emptyText: 'Tool Description',	
	    });
	    
	    Ext.apply (config, {
		width: 300,
		items: [
		    toolTitle,
		    toolType,
		    toolDesc,
		],
		buttons: [
		    new Ext.Button ({
			text: 'Cancel',
			handler: function (b) {
			    thisWin.close ();
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
				    thisPanel.addChild (resp);
			    };
			    
			    Ext.Ajax.request ({
				method: 'POST',
				url: '/' + hs.application + '/tool/dev/create',
				success: createNewTool,
				params: {
				    name: toolTitle.getValue (),
				    type: toolType.getValue ().inputValue,
				    desc: toolDesc.getValue (),
				},
			    });
			    thisWin.close ();
			},
		    }),
		],
	    });
	    hs.win.DevCreate.superclass.constructor.call (this, config);
	},
    }),
    DevWin: Ext.extend (Ext.Window, {
	//constructor: function (id, thisPanel, tool, devPerm, config) {
	constructor: function (tool, thisPanel, devPerm, toolPanel, config) {
	    var dirtyFlag = true;

	    var mode;

	    if (!config)
		config = {};

	    var thisWin = this;

	    var runButton = new Ext.Button ({
		text: 'Run Tool',
		handler: function () {
		    toolPanel.tabPanel.setActiveTab (toolPanel.toolnum);
		    toolPanel.panel.dropTool (tool);
		    thisWin.hide ();
		},
	    });

	    var codeDesc = new Ext.Panel ({
		title: 'Overview',
		hideBorders: true,
		autoScroll: true,		
		buttons: [
		    runButton,
		],
	    });

	    var viewPanel = new Ext.Panel ({
		title: 'View Code',
		hideBorders: true,
		autoScroll: true,
		listeners: {
		    show: function () {
			if (dirtyFlag) {
			    removeCode ();
			    showCode ();
			}
		    },
		},
	    });

	    var removeCode = function () {
		viewPanel.removeAll ();
	    };

	    var showCode = function () {
		dirtyFlag = false;
		var populateView = function (data) {
		    var code = JSON.parse (data.responseText);
		    viewPanel.add ({
			html: code.text,
		    });

		    codeDesc.add ({
			html: '<b>Name:</b> ' + code.name,
		    });
		    codeDesc.add ({
			html: '<b>Type:</b> ' + code.type,
		    });
		    codeDesc.add ({
			html: '<b>Description:</b> ' + code.description,
		    });

		    codeDesc.doLayout ();
		    viewPanel.doLayout ();
		};

		Ext.Ajax.request ({
		    method: 'GET',
		    url: '/' + hs.application + '/tool/tool/read',		
		    success: populateView,
		    params: {
			'id': tool.id
		    },
		});
	    };
	    showCode ();

	    var items;

	    if (devPerm) {

		var publishTool = function (data) {
		    //toolSide.appendChild (tool.name, tool.id, tool.type);
		    tool.remove ();
		    thisWin.close ();
		};

		var pubButton = new Ext.Button ({
		    text: 'Publish Tool',
		    handler: function (b) {
			Ext.Ajax.request ({
			    method: 'GET',
			    url: '/' + hs.application + '/tool/dev/publish',		
			    success: publishTool,
			    params: {
				'id': tool.id
			    },
			});
		    },
		});

		var refreshCode = function (data) {
		    dirtyFlag = true;
		};

		var areaId = 'editTool' + hs.util.counter;
		hs.util.counter ++;

		function savedCode (data) {
		    Ext.MessageBox.alert ('Save', 'Your code has been saved.');
		    refreshCode ();
		};

		var saveButton = new Ext.Button ({
		    text: 'Save Tool',
		    handler: function () {
			Ext.Ajax.request ({
			    method: 'POST',
			    url: '/' + hs.application + '/tool/dev/save',
			    success: savedCode,
			    params: {
				id: tool.id,
				text: editAreaLoader.getValue (areaId),
			    },
			});
		    },
		});
		
		var editPanel = new Ext.Panel ({
		    title: 'Edit Code',
		    height: 500,
		    html: '<textarea style="width: 100%; height: 100%;" id="' + areaId  + '"></textarea>',
		    buttons: [
			saveButton,
		    ],
		    listeners: {
			afterrender: function () {
			    var populateTextArea = function (data) {
				editAreaLoader.setValue (areaId, data.responseText);
			    };

			    editAreaLoader.init({
				id : areaId,
				syntax: "python",
				start_highlight: false,
			    });

			    Ext.Ajax.request ({
				method: 'GET',
				url: '/' + hs.application + '/tool/dev/code',		
				success: populateTextArea,
				params: {
				    'id': tool.id
				},
			    });
			},
			beforehide: function () {
			    editAreaLoader.hide (areaId);
			},
			show: function () {
			    editAreaLoader.show (areaId);
			},
		    },
		});
		
		var pubPanel = new Ext.Panel ({
		    title: 'Publish',
		    height: 500,
		    buttons: [
			pubButton,
		    ],
		});

		items = [
		    codeDesc,
		    viewPanel,
		    editPanel,
		    pubPanel,
		];
	    }

	    else {
		items = [
		    codeDesc,
		    viewPanel,
		];
		if (hs.user.dev) {
		    var forkButton = new Ext.Button ({
			text: 'Fork',
			handler: function () {
			    Ext.Ajax.request ({
				method: 'POST',
				url: '/' + hs.application + '/tool/dev/fork',
				success: function (data) {
				    var new_tool = JSON.parse (data.responseText);
				    devSide.appendChild (new_tool.name,
							 new_tool.id,
							 new_tool.type);
				    devSide.doLayout ();
				},
				params: {
				    id: tool.id,
				},
			    });
			},
		    });

		    var forkPanel = new Ext.Panel ({
			title: 'Fork',
			height: 500,
			buttons: [
			    forkButton,
			],
		    });
		
		    items.push (forkPanel);
		}
	    }

	    var mainPanel = new Ext.TabPanel ({
		activeTab: 0,
		items: items,
	    });
		
	    Ext.apply (config, {
		layout: 'fit',
		autoScroll: true,
		maximizable: true,
		items: [
		    mainPanel,
		],
	    });
 
	    hs.win.DevWin.superclass.constructor.call (this, config);

	},
    }),
};