hs.win = {
    DevWin: Ext.extend (Ext.Window, {
	constructor: function (id, toolSide, devSide, tool, devPerm, toolPanel, config) {
	    var dirtyFlag = true;

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
			html: '<b>Description:</b> ' + code.desc,
		    });

		    codeDesc.doLayout ();
		    viewPanel.doLayout ();
		};

		var mode = '';
		
		Ext.Ajax.request ({
		    method: 'GET',
		    url: '/' + hs.application + '/tool/read',		
		    success: populateView,
		    params: {
			'id': id
		    },
		});
	    };
	    showCode ();

	    var items;

	    if (devPerm) {

		var publishTool = function (data) {
		    toolSide.appendChild (tool.name, tool.id, tool.type);
		    tool.remove ();
		    thisWin.close ();
		};

		var pubButton = new Ext.Button ({
		    text: 'Publish Tool',
		    handler: function (b) {
			Ext.Ajax.request ({
			    method: 'GET',
			    url: '/' + hs.application + '/tool/publish',		
			    success: publishTool,
			    params: {
				'id': id
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
			    url: '/' + hs.application + '/tool/dev_save',
			    success: savedCode,
			    params: {
				id: id,
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
				url: '/' + hs.application + '/tool/dev_code',		
				success: populateTextArea,
				params: {
				    'id': id
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
				url: '/' + hs.application + '/tool/dev_fork',
				success: function (data) {
				    var new_tool = JSON.parse (data.responseText);
				    devSide.appendChild (new_tool.name,
							 new_tool.id,
							 new_tool.type);
				    devSide.doLayout ();
				},
				params: {
				    id: id,
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