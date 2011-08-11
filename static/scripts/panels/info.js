hs.info = {
    NPRPanel: Ext.extend (Ext.Panel, {
	constructor: function (config) {
	    if (!config)
		config = {};

	    this.populate = function (d) {
		var element = this;
		Ext.Ajax.request ({
		    url: '/' + hs.application + '/sources/npr',
		    method: 'GET',
		    params: {
			disease: d,
		    },
		    success: function (data) {
			element.removeAll ();
			var ob = JSON.parse (data.responseText);
			console.log (ob);
			var stories = ob.list.story;
			console.log (stories);
			for (var i = 0; i < stories.length; i ++) {
			    var html = '<div><a href="' + stories[i].link[2]['$text'] + '">' + stories[i].title['$text']  + '</a><br />' + stories[i].teaser['$text'] + '</div>';
			    element.add ({
				border: false,
				padding: 10,
				html: html,
			    });
			}
			element.doLayout ();
		    },
		    failure: function () {
			console.log ('NPR API returned error');
		    },
		});
	    };
	    
	    Ext.apply (config, {
		region: 'west',
		title: 'NPR',
		autoScroll: true,
		width: 400,
		padding: 10,
	    });
	    hs.info.NPRPanel.superclass.constructor.call (this, config);
	},
    }),
    WikiPanel: Ext.extend (hs.util.IFramePanel, {
	constructor: function (config) {
	    var thisPanel = this;
            if (!config)
		config = {}

	    this.populate = function (d) {
		this.src ('/' + hs.application + '/sources/wiki?disease=' + d);
	    };

	    Ext.apply (config, {
		title: 'Wikipedia',
		region: 'center',
		autoScroll: true,
		padding: 0,
		listeners: {
		    show: function (event) {
			//thisPanel.populate ('malaria');
		    },
		},
	    });
	    hs.info.WikiPanel.superclass.constructor.call (this, config);
	},
    }),
    LitPanel: Ext.extend (Ext.Panel, {
	constructor: function (config) {
	    var keywords;
	    var maps;
	    
	    var store = new Ext.data.JsonStore ({

	    });

	    /*var keyword_root = new Ext.tree.AsyncTreeNode({
		expanded: true,
		children: childNodes,
	    });*/

	    var KeywordRecord = Ext.data.Record.create ([
		'kw',
		'count',
		'numMaps',
		'maps',
	    ]);

	    var keywordCols = new Ext.grid.ColumnModel ([
		 {
		     id: 'kw',
		     header: 'Keyword',
		     sortable: true,
		     dataIndex: 'kw'
		 },
		 {
		     id: 'count',
		     header: 'Rank',
		     sortable: true,
		     dataIndex: 'count'
		 },
		 {
		     id: 'numMaps',
		     header: 'Maps',
		     sortable: true,
		     dataIndex: 'numMaps'
		 },
	    ]);

	    var mapList = [];
	    
	    this.populate = function (d) {
		Ext.Ajax.request ({
		    url: '/' + hs.application + '/geodata/kw',
		    method: 'GET',
		    params: {
			d: d,
		    },
		    success: function (data) {
			mapList = [];
			var ob = JSON.parse (data.responseText);
			records = [];
			store.removeAll ();
			for (var i = 0; i < ob.length; i ++) {
			    mapList.push (ob[i]['maps']);
			    records.push (new KeywordRecord (ob[i]));
			}
			console.log (ob, mapList);
			store.add (records);
			keywords.reconfigure (store, keywordCols);
		    },
		    failure: function () {
			console.log ('Lit call went wrong');
		    },
		});
	    };

	    var addMapNode = function (ob) {
		root.appendChild (new hs.tree.Node ('maps', ob));
	    };

	    var root = new Ext.tree.AsyncTreeNode({
		expanded: true,
		children: [],
	    });
	    
	    maps = new Ext.tree.TreePanel ({
		title: 'Maps',
		rootVisible: false,
		root: root,
		expanded: true,
		enableDrag: true,
		columnWidth: .75,
		dragConfig: {
		    ddGroup: 'layers',
		    dragAllowed: true,
		    dropAllowed: false,
		},
	    });

	    keywords = new Ext.grid.GridPanel ({
		title: 'Keywords',
		store: store,
		columns: keywordCols,
		columnWidth: .25,
		autoHeight: true,
		listeners: {
		    cellclick: function (el, rowIndex, colIndex, event) {
			root.removeAll ();
			var m = mapList[rowIndex];
			for (var i = 0; i < m.length; i ++) {
			    addMapNode (m[i]);
			}
			maps.doLayout ();
		    }
		},
	    });

	    if (!config)
		config = {};

	    Ext.apply (config, {
		title: 'Automated',
		layout: 'column',
		hideBorders: true,
		items: [
		    keywords,
		    maps,
		],
	    });

	    hs.info.LitPanel.superclass.constructor.call (this, config);
	},
    }),
    MapPanel: Ext.extend (Ext.tree.TreePanel, {
	constructor: function (config) {
	    var root = new Ext.tree.TreeNode({
		expanded: true,
		children: [],
	    });

	    if (!config)
		config = {};
	    Ext.apply (config, {
		title: 'Maps',
		rootVisible: false,
		root: root,
		expanded: true,
		collapsible: false,
		enableDrag: true,
		dragConfig: {
		    ddGroup: 'layers',
		},
		autoScroll: true,
	    });

	    var thisPanel = this;

	    var addMaps = function (data) {
		var maps = JSON.parse (data.responseText);
		for (var i = 0; i < maps.length; i ++) {
		    root.appendChild (new hs.tree.Node ('maps', maps[i]));
		}
		thisPanel.doLayout ();
	    };

	    Ext.Ajax.request ({
		method: 'GET',
		url: '/' + hs.application + '/geodata/maps',
		success: addMaps,
	    })

	    hs.info.MapPanel.superclass.constructor.call (this, config);
	},
    }),
    Panel: Ext.extend (Ext.Panel, {
	constructor: function (config) {

	    var nprPanel = new hs.info.NPRPanel ();

	    var wikiPanel = new hs.info.WikiPanel ();

	    var selectBox = new Ext.form.ComboBox ({
		region: 'north',
		store: ['malaria', 'cholera'],
		//emptyText: 'malaria',
	    });

	    //var litPanel = new hs.info.LitPanel ();

	    //litPanel.populate ('malaria');
	    wikiPanel.populate('malaria');
	    nprPanel.populate('malaria');	    

	    var mainPanel = new Ext.Panel ({
		title: 'Info',
		layout: 'border',
		region: 'center',
		items: [
		    wikiPanel,
		    nprPanel,
		],
	    });
	    
	    var dataMapsPanel = new hs.info.MapPanel ();
	    
	    var tabsPanel = new Ext.TabPanel ({    
		region: 'center',
		activeTab: 0,
		items: [
		    mainPanel,
		    /*{
			title: 'Tools',
			html: '',
		    },
		    dataMapsPanel,
		    {
			title: 'Research',
			html: '',  
		    },
		    litPanel,*/
		]
	    });
	    
	    var submitButton = new Ext.Button ({
		text: 'Submit',
		handler: function () {
		    //litPanel.populate (selectBox.getValue ());
		    wikiPanel.populate(selectBox.getValue ());
		    nprPanel.populate(selectBox.getValue ());
		},
	    });
	    
	    var chooseDisease = new Ext.Panel ({
		region: 'north',
		autoHeight: true,
		layout: 'hbox',
		items: [
		    selectBox,
		    submitButton,
		],
	    });
	    
	    var topPanel = new Ext.Panel ({
		region: 'north',
		autoHeight: true,
		items: [
		    chooseDisease,
		    //mapPanel,
		],
	    });

	    this.getMap = function () {
		return map;
	    };
	    
	    if (!config)
		config = {};
	    Ext.apply (config, {
		items: [
		    //topPanel,
		    chooseDisease,
		    tabsPanel,
		],
	    });
	    hs.info.Panel.superclass.constructor.call (this, config);
	},
    }),
};