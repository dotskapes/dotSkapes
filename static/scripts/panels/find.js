hs.find = {
    Panel: Ext.extend (Ext.Panel, {
	constructor: function (config) {
	    if (!config)
		config = {};

	    var Filter = Ext.extend (Ext.Button, {
		constructor: function (name, g) {
		    Filter.superclass.constructor.call (this, {
			text: name,
			enableToggle: true,
			toggleGroup: 'filter',
			handler: function () {
			    g.reload (name);
			},
		    });
		},
	    });

	    var dataGrid = new hs.grid.Panel ({
		region: 'center',
		datatype: 'maps',
		load_public: true,
		viewConfig: {
		    forceFit: true,
		},
	    });

	    var rec = new Ext.form.Checkbox ({
		boxLabel: 'Detector',
		listeners: {
		    check: function (box, event) {
			dataGrid.recommend (box.getValue ());
			dataGrid.reload (null);
		    }
		},
	    });

	    var keywordFilter = function (g, det, config) {
		if (!config)
		    config = {};
		Ext.apply (config, {
		    listeners: {
			specialkey: function (field, e) {
			    console.log ("EVENT");
			    if (e.getKey () == e.ENTER) {
				g.recommend (det.getValue ());
				g.keyword (field.getValue ());
			    }
			},
		    },
		});
		return new Ext.form.TextField (config);
	    };
	    
	    var top_menu = new Ext.Toolbar ({
		height: 30,
		items: [
		    keywordFilter (dataGrid, rec),
		    rec,
		],
	    });

	    var sub_menu = new Ext.Toolbar ({
		height: 'autoHeight',
		items: [
		    new Filter ('maps', dataGrid),
		    new Filter ('tools', dataGrid),
		    new Filter ('dev_tools', dataGrid),
		],
	    });

	    var menus = new Ext.Panel ({
		region: 'north',
		height: 'autoHeight',
		items: [
		    top_menu,
		    sub_menu,
		],
	    });

	    Ext.apply (config, {
		region: 'center',
		layout: 'border',
		items: [
		    menus,
		    dataGrid,
		],
	    });
	    hs.find.Panel.superclass.constructor.call (this, config);
	},
    }),
};