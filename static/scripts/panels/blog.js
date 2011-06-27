hs.blog = {
    Panel: Ext.extend (Ext.Panel, {
	constructor: function (config) {
	    var this_panel = this;
	    if (!config)
		config = {};
	    Ext.apply (config, {
		title: 'Blog',
	    });

	    Ext.Ajax.request ({
		method: 'GET',
		url: hs.url ('plugin_wiki', 'all'),
		success: function (data) {
		    var entries = JSON.parse (data.responseText);
		    for (var i = 0; i < entries.length; i ++) {
			this_panel.add (new Ext.Panel ({
			    title: entries[i].title,
			    html: entries[i].html,
			    collapsible: true,
			}));
			this_panel.doLayout ();
		    }
		},
	    });

	    hs.blog.Panel.superclass.constructor.call (this, config);
	},
    }),
};