hs.create = {
    Panel: Ext.extend (Ext.Panel, {
	constructor: function (config) {
	    if (!config) 
		config = {};

	    var areaId = 'createTool';

	    /*var toolParam = function () {
		var paramName = new Ext.form.Field ({
		    value: 'Name',
		});
		
		var paramSymbol = new Ext.form.Field ({
		    value: 'Symbol',
		});

		var paramType = new Ext.form.ComboBox ({
		    store: [
			['text', 'Text'],
			['poly_map', 'Polygon Map'],
			['point_map', 'Point Map'],
			['agg', 'Aggregation'],
		    ],
		});
		
		var panel = new Ext.Panel ({
		    layout: 'hBox',
		    items: [
			paramName,
			paramSymbol,
			paramType,
		    ],
		});
		return panel;
	    }

	    var titleBar = new Ext.form.Field ({
		value: 'Tool Title',
	    });

	    var analysisType = new Ext.form.RadioGroup ({
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

	    var addParam = new Ext.Button ({
		text: 'Add Param',
	    });

	    var leftPanel = new Ext.Panel ({
		region: 'west',
		width: 600,
		items: [
		    titleBar,
		    analysisType,
		    toolParam (),
		],
	    });

	    var rightPanel = new Ext.Panel ({
		region: 'center',

	    });*/

	    var saveButton = new Ext.Button ({
		text: 'Save',
		handler: function () {
		    Ext.Ajax.request ({
			method: 'POST',
			url: '/' + hs.application + '/tool/create',
			params: {
			    title: titleBar.getValue (),
			    text: editAreaLoader.getValue (areaId),
			    type: analysisType.getValue ().inputValue,
			},
		    });
		},
	    });

	    var rTemplate = '\
# Add R code here. use the function HS_RequestParam (key, name, type)\n\
# Use this function to insert parameters from the main applciation to your tool\n\
';
	    
	    var rButton = new Ext.Button ({
		text: 'Add R Template',
		handler: function () {
		    editAreaLoader.setValue (areaId, rTemplate);
		},
	    });

	    var pyTemplate = '\
# Add parameters here. Each parameter is of the form\n# (param_name, param_title, param_type)\n\
cargs = []\n\
\n\
# Implement tool function here. Parameters are accessible as attr[param_name].\n\
# The return type should be the MIME type of the result.\n\
# An IO Stream attr[\'file\'] is provided to store the result.\n\
def ctool (**attr):\n\
    pass';

	    var pyButton = new Ext.Button ({
		text: 'Add Python Template',
		handler: function () {
		    editAreaLoader.setValue (areaId, pyTemplate);
		},
	    });

	    var titleBar = new Ext.form.Field ({
		value: 'Tool Title',
		columnWidth: .25,
	    });

	    var analysisType = new Ext.form.RadioGroup ({
		columnWidth: .25,
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
	    
	    var topPanel = new Ext.Panel ({
		height: 35,
		region: 'north',
		layout: 'column',
		items: [
		    titleBar,
		    analysisType,
		],
	    });

	    var textArea = new Ext.Panel ({
		region: 'center',
		html: '<textarea style="width: 100%; height: 100%;" id="' + areaId  + '"></textarea>',
	    });

	    Ext.apply (config, {
		layout: 'border',
		region: 'center',
		items: [
		    topPanel,
		    textArea,
		],
		buttons: [
		    rButton,
		    pyButton,
		    saveButton,
		],
		listeners: {
		    afterlayout: function () {
			console.log ('Size', this.getInnerHeight (), this.getInnerWidth ());
		    },
		    afterrender: function () {
			editAreaLoader.init({
			    id : areaId,
			    syntax: "python",
			    start_highlight: true,
			});
		    },
		    beforehide: function () {
			editAreaLoader.hide (areaId);
		    },
		    show: function () {
			editAreaLoader.show (areaId);
		    },
		},
		/*layout: 'border',
		items: [
		    leftPanel,
		    rightPanel,
		],*/
	    });

	    hs.create.Panel.superclass.constructor.call (this, config);
	},
    }),
};