hs.win.Result = Ext.extend (Ext.Window, {
    constructor: function (node, config) {
	var perm = 0;
	var text;
	var urlText;
	var urlPanel;

	var result_id = node.id;
	var title = node.name;

	var pubURL = 'Public URL: ' + window.location.host + '/healthscapes/tool/result/load?id=' + result_id;
		
	function togglePerm  () {
	    if (perm) {
		text = 'Make Result Private';
		perm = 0;
		urlText = pubURL;
	    }
	    else {
		text = 'Make Result Public';
		perm = 1;
		urlText = '&nbsp;';
	    }
	};
	togglePerm ();
	
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
		urlPanel.update (urlText);
		b.setText (text);
	    },
	});
	
	var exportButton = new Ext.Button ({
	    text: 'Export',
	    handler: function (b, e) {
		Ext.Ajax.request ({
		    method: 'GET',
		    url: hs.url ('tool', 'result', ['export_available']),
		    params: {
			id: result_id,
		    },
		    success: function  (data) {
			var types = JSON.parse (data.responseText);
			var selections = [];
			for (var i = 0; i < types.length; i ++) {
			    selections.push ({
				inputValue: types[i].id,
				boxLabel: types[i].name,
				name: 'export_mode',
			    });
			}
			var radio = new Ext.form.RadioGroup  ({
			    items: selections,
			    width: 200,
			});

			var input = new Ext.form.TextField ({
			    emptyText: 'Filename',
			    width: 200,
			});

			var win = new Ext.Window ({
			    title: 'Export Result',
			    width: 200,
			    items: [
				radio,
				input,
			    ],
			    buttons: [
				new Ext.Button ({
				    text: 'Export',
				    handler: function (b, e) {
					window.location = hs.url ('tool', 'result', ['export'], {
					    id: result_id,
					    mode: radio.getValue ().inputValue,
					    filename: input.getValue (),
					});
				    },
				}),
			    ],
			});
			win.show ()
		    },
		});
	    },
	});

	var result = new hs.util.IFramePanel ({
	    region: 'center',
	}, '/' + hs.application + '/tool/result/load?id=' + result_id);
	
	urlPanel = new Ext.Panel ({
	    region: 'south',
	    height: 'autoHeight',
	    padding: 10,
	    html: '&nbsp;',
	    //hidden: (perm == 1),
	});

	Ext.apply (config, {
	    layout: 'border',
	    width: 800,
	    height: 600,
	    hideBorders: true,
	    title: title,
	    items: [
		result,
		urlPanel,
	    ],
	    buttons: [
		exportButton,
		publicButton,
	    ],
	});
	hs.win.Result.superclass.constructor.call(this,  config);
    },
});