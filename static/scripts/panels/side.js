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
		    var win = new hs.win.DevCreate (thisPanel);
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
			var win = new hs.win.DevWin (node, thisPanel, true, toolPanel, {
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
    ResultPanel: Ext.extend (hs.tree.Panel, {
	constructor: function (data, config) {
	    if (!config)
		config = {};

	    Ext.apply (config, {
		datatype: 'results',
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
			
			var result_id = node.id;
			var title = node.filename;

			var publicButton = new Ext.Button ({
			    text: text,
			    handler: function (b, e) {
				Ext.Ajax.request ({
				    method: 'GET',
				    url: '/' + hs.application + '/tool/result/publish',
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
			
			var result = new hs.util.IFramePanel ({
			    region: 'center',
			}, '/' + hs.application + '/tool/result/load?id=' + result_id);

			var urlPanel = new Ext.Panel ({
			    region: 'south',
			    border: false,
			    height: 'autoHeight',
			    html: 'Public URL: ' + window.location + '/healthscapes/tool/get_result?id=' + result_id,
			    hidden: (perm == 1),
			});

			var w = new Ext.Window ({
			    layout: 'border',
			    width: 800,
			    height: 600,
			    title: title,
			    closeAction: 'close',
			    items: [
				result,
				urlPanel,
			    ],
			    buttons: [
				publicButton,
			    ],
			    listeners: {
				render: function (el) {
				    /*var panel = new Ext.Panel ({
					html: '<iframe style="margin: 0px; padding: 0px; border: none;" width="' + (775)  + '" height="' + (500)  + '" src="/' + hs.application + '/tool/result/load?id=' + result_id + '"></iframe>',

				    });

				    urlPanel = new Ext.Panel ({
					html: 'Public URL: ' + window.location + '/healthscapes/tool/get_result?id=' + result_id,
					hidden: (perm == 1),
				    });

				    this.add (panel);
				    this.add (urlPanel);
				    this.doLayout ();*/
				},
			    },
			});
			w.show ();
		    },
		},
	    });
	    hs.side.ResultPanel.superclass.constructor.call (this, data, config);
	},
    }),
};