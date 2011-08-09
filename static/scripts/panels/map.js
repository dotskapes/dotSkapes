hs.map = {
    Panel: Ext.extend (Ext.Panel, {
	constructor: function (config) {
	    var mapPanel;
	    var toolbar;
	    var attrPanel;
	    var sidePanel;
	    var thisPanel = this;
	    var activeLayers = {};
	    var layers = {};
	    var select = {};
	    var control = {};
	    if (!config)
		config = {};

	    var selectControl;
	    var selectLayer = new OpenLayers.Layer.Vector("Selection", {styleMap: 
									new OpenLayers.Style(OpenLayers.Feature.Vector.style["select"])
								       });
	    
	    /*var defaultStyle = new OpenLayers.StyleMap ({
		pointRadius: 2,
		fillColor: '#ee9900',
		fillOpacity: .4,
		strokeColor: '#ee9900',
	    });*/
	    
	    this.getVisibleLayers = function () {
		var nodeList = [];
		for (key in activeLayers) {
		    nodeList.push (activeLayers[key]);
		}
		return nodeList;
	    };

	    this.addMap = function (node) {
		var map = mapPanel.getMap ();
		if (!(node.filename in layers)) {
		    layers[node.filename] = new OpenLayers.Layer.WMS (
			"Map",
			'/' + hs.application + '/geoserver/ows?ID=' + node.id,
			{
			    SERVICE: 'WMS',
			    layers: node.prefix + ':' + node.filename,
			    transparent: true,
			    format: "image/png",
			    projection: 'EPSG:900913',
			    //sld: 'http://zk.healthscapes.org/healthscapes/static/test.xsd',
			    styles: null,
			},
			{
			    isBaseLayer: false,
			    displayOutsideMaxExtent: true,
			}
		    );
		    /*layers[node.filename] = new OpenLayers.Layer.WMS (
			"Map",
			'/' + hs.application + '/geoserver/filter?ID=' + node.id,
			{
			    SERVICE: 'WMS',
			    layers: node.prefix + ':' + node.filename,
			    transparent: true,
			    format: "image/png",
			    projection: 'EPSG:900913',
			    //sld: 'http://zk.healthscapes.org/healthscapes/static/test.xsd',
			    //styles: null,
			    FIELD: 'pop_admin',
			    MODE: 'gt',
			    VALUE: 1000000,
			},
			{
			    isBaseLayer: false,
			    displayOutsideMaxExtent: true,
			}
		    );*/
		    /*layers[node.filename] = new OpenLayers.Layer.WMS (
			"Map",
			'/' + hs.application + '/geoserver/choropleth?ID=' + node.id,
			{
			    SERVICE: 'WMS',
			    layers: node.prefix + ':' + node.filename,
			    transparent: true,
			    format: "image/png",
			    projection: 'EPSG:900913',
			    //sld: 'http://zk.healthscapes.org/healthscapes/static/test.xsd',
			    //styles: null,
			    FIELD: 'pop_admin',
			    LOW_COLOR: '0xff0000',
			    HIGH_COLOR: '0x00ff00',
			},
			{
			    isBaseLayer: false,
			    displayOutsideMaxExtent: true,
			}
		    );*/

		    /*layers[node.filename].events.register ('click', this, function (e) {
			console.log ('Event', e);
		    });*/
		    
		    /*Ext.Ajax.request ({
			method: 'GET',
			url: hs.url ('geoserver', 'choropleth.xsd'),
			params: {
			    ID: node.id,
			    FIELD: 'pop_admin',
			    LOW_COLOR: '0xff0000',
			    HIGH_COLOR: '0x00ff00',
			},
			success: function (data) {
			    layers[node.filename] = new OpenLayers.Layer.WMS (
				"Map",
				'/' + hs.application + '/geoserver/ows?ID=' + node.id,
				{
				    SERVICE: 'WMS',
				    layers: node.prefix + ':' + node.filename,
				    transparent: true,
				    format: "image/png",
				    projection: 'EPSG:900913',
				    SLD_NAME: JSON.parse (data.responseText).id,
				},
				{
				    isBaseLayer: false,
				    displayOutsideMaxExtent: true,
				    unsupportedBrowsers: [],
				}
			    );
			    map.addLayer (layers[node.filename]);
			    activeLayers[node.filename] = node;
			    attrPanel.loadMap (node);
			},
		    });
		    return;*/

		    control[node.filename] = new OpenLayers.Control.GetFeature({
			protocol: OpenLayers.Protocol.WFS.fromWMSLayer(layers[node.filename], {
			    srsName: 'EPSG:900913',
			}),
			strategies: [
			    new OpenLayers.Strategy.BBOX (),
			],
			/*protocol: new OpenLayers.Protocol.WFS.v1_1_0 ({
			    url: '/' + hs.application + '/geoserver/wfs?id=' + node.id,
			    featureType: node.filename,
			    featureNS: node.prefix,
			    srsName: 'EPSG:900913',
			}),*/
			box: true,
			hover: false,
			multipleKey: "shiftKey",
			toggleKey: "shiftKey",
		    });

		    control[node.filename].events.register("featureselected", this, function(e) {
			selectLayer.addFeatures([e.feature]);
		    });
		    control[node.filename].events.register("featureunselected", this, function(e) {
			selectLayer.removeFeatures([e.feature]);
		    });

		    map.addControl (control[node.filename]);
		    layers[node.filename].events.register ('loadend', layers[node.filename], function (event) {
			attrPanel.loadMap (node);
		    });

		}
		//else {
		//    attrPanel.loadMap (node);
		//}
		selectControl = control[node.filename];
		map.addLayer (layers[node.filename]);
		activeLayers[node.filename] = node;
	    };

	    this.removeMap = function (node) {
		var map = mapPanel.getMap ();
		map.removeLayer (layers[node.filename]);
		delete activeLayers[node.filename];
		//map.removeLayer (select[node.filename]);
		//control[node.filename].deactivate ();
	    };
	    
	    Ext.apply (config, {
		layout: 'border',
		listeners: {
		    render: function (e) {
			mapPanel = new hs.map.MapPanel ({
			    region: 'center',
			});

			var map = mapPanel.getMap ();

			var filterButton = new hs.map.FilterButton (thisPanel);

			toolbar = new Ext.Toolbar ({
			    region: 'north',
			    height: 30,
			    items: [
				new Ext.Button ({
				    text: "Select Subset",
				    enableToggle: true,
				    listeners: {
					toggle: function (b, toggle) {
					    if (toggle) {
						map.addLayer (selectLayer);
						selectControl.activate ();
					    }
					    else {
						selectLayer.removeAllFeatures();
						map.removeLayer (selectLayer);
						selectControl.deactivate ();
					    }
					},
				    },
				}),
				filterButton,
				new hs.map.BaseLayer (mapPanel.getMap ()),
			    ],
			});

			attrPanel = new hs.map.AttrPanel (mapPanel.getMap (), {
			    height: 200,
			    region: 'south',
			    viewConfig: {
				forceFit: true,
			    },
			});
			
			thisPanel.add (mapPanel);
			thisPanel.add (toolbar);
			thisPanel.add (attrPanel);
		    },
		},
	    });
	    hs.map.Panel.superclass.constructor.call (this, config);
	},
    }),
    MapPanel: Ext.extend (GeoExt.MapPanel, {
   	constructor: function (config) {
	    if (!config)
		config = {};

	    var map = new OpenLayers.Map("HS Map", {
		projection: new OpenLayers.Projection("EPSG:900913"),
		displayProjection: new OpenLayers.Projection("EPSG:4326"),
	    });

	    /*var base = new OpenLayers.Layer.Google ('Google Base Layer', {
		type: google.maps.MapTypeId.TERRAIN
	    });
	    map.addLayer (base);
	    map.removeLayer (base);
	    
	    var base = new OpenLayers.Layer.OSM ('OSM Base Layer');
	    map.addLayer (base);*/

	    this.getMap = function () {
		return map;
	    };
	    
	    Ext.apply (config, {
		map: map,
		//buttons: [
		//    saveButton,
		//],
		listeners: {
		    afterlayout: function () {
			var center = new OpenLayers.LonLat (-55.0, -10.0);
			var proj4326 = new OpenLayers.Projection('EPSG:4326');
			var projection_current = new OpenLayers.Projection('EPSG:900913');
			center.transform(proj4326, projection_current);
			map.setCenter (center, 4);
		    },
		},
	    });
	    hs.map.MapPanel.superclass.constructor.call (this, config);
	},
    }),
    AttrPanel: Ext.extend (Ext.grid.GridPanel, {
	constructor: function (map, config) {
	    var thisPanel = this;
	    var current_map;
	    var fields = [];
	    var cols = {};
	    var colModel;

	    var start = 0;
	    var limit = 50;

	    if (!config)
		config = {};

	    var reloadStore = function () {
		var store = new Ext.data.JsonStore ({
		    root: 'features',
		    autoLoad: true,
		    fields: fields,
		    url: hs.url ('geodata', 'read', [], {
			id: cols.id,
			start: start,
			limit: limit,
		    }),
		});
		thisPanel.reconfigure (store, colModel);
	    };

	    var setNewModel = function (data) {
		fields = [];
		cols = JSON.parse (data.responseText);
		var colList = [];
		for (var i = 0; i < cols.columns.length; i ++) {
		    colList.push ({header: cols.columns[i]});
		    fields.push (cols.columns[i]);
		}

		colModel = new Ext.grid.ColumnModel ({
		    defaults: {
			sortable: true,
		    },
		    columns: colList,
		});

		reloadStore ();
	    };

	    var requestCols = function (map_id) {
		Ext.Ajax.request ({
		    method: 'GET',
		    url: '/' + hs.application + '/geodata/columns',
		    success: setNewModel,
		    params: {
			id: map_id,
		    },
		});
	    }

	    this.loadMap = function (map_ob) {
		if (current_map == map_ob)
		    return;
		current_map = map_ob;
		requestCols (map_ob.id);
	    };

	    var overlays = {};

	    Ext.apply (config, {
		title: 'Attributes',
		collapsible: true,
		colModel: new Ext.grid.ColumnModel ({}),
		sm: new Ext.grid.RowSelectionModel ({
		    listeners: {
			rowselect: function (model, id, record) {
			    overlays[record.id] = new OpenLayers.Layer.Vector ("Overlay", {
				strategies: [new OpenLayers.Strategy.Fixed ()],
				protocol: new OpenLayers.Protocol.HTTP ({
				    url: '/' + hs.application + '/geoserver/wfs',
				    format: new OpenLayers.Format.GML (),
				    params: {
					outputformat: 'GML2',
					ID: current_map.id,
					request: 'GetFeature',
					featureID: record.id,
					srsName: 'EPSG:900913',
				    },
				}),
			    });
			    map.addLayer (overlays[record.id]);
			},
			rowdeselect: function (model, id, record) {
			    map.removeLayer (overlays[record.id]);
			}
		    },
		}),
		store: [],
		bbar: [
		    new Ext.Button ({
			text: 'Prev',
			handler: function () {
			    if (start > 0)
				start -= limit;
			    reloadStore ();
			},
		    }),
		    new Ext.Button ({
			text: 'Next',
			handler: function () {
			    //if (start < attr_max)
			    start += limit;
			    reloadStore ();
			},
		    }),
		],
	    });
	    
	    hs.map.AttrPanel.superclass.constructor.call (this, config);
	},
    }),
    FilterButton: Ext.extend (Ext.Button, {
	constructor: function (mapPanel, config) {
	    if (!config)
		config = {};

	    Ext.apply (config, {
		text: 'Filter Map',
		listeners: {
		    click: function (b) {
			layers = mapPanel.getVisibleLayers ();
			
			var field_data = [];
			for (var i = 0; i < layers.length; i ++) {
			    field_data.push ([layers[i], layers[i].name]);
			}
			var layer_select = new Ext.form.ComboBox ({
			    store: new Ext.data.ArrayStore ({
				fields: [
				    'node',
				    'node_name',
				],
				data: field_data,
			    }),
			    valueField: 'node',
			    displayField: 'node_name',
			    mode: 'local',
			    triggerAction: 'all',
			    width: 250,
			    listeners: {
				select: function (cb, record, index) {
				    Ext.Ajax.request ({
					method: 'GET',
					url: hs.url ('geodata', 'columns'),
					params: {
					    id: record.data.node.id,
					},
					success: function (data) {
					    console.log (data.responseText);
					}
				    });
				},
			    }
			});

			var filter_slider = new Ext.slider.MultiSlider ({
			    disabled: true,
			    minValue: 0,
			    maxValue: 1,
			});

			var win = new Ext.Window ({
			    width: 300,
			    height: 200,
			    title: 'Create Filter',
			    items: [
				layer_select,
				filter_slider,
			    ],
			});
			win.show ();
		    },
		},
	    });
	    hs.map.FilterButton.superclass.constructor.call (this, config);
	    
	},
    }),
    BaseLayer: Ext.extend (Ext.Button, {
	constructor: function (map) {
	    var thisButton = this;

	    var baseLayers = {
		/*'none': new OpenLayers.Layer("No Base Layer", {
		    isBaseLayer: true,
		    'displayInLayerSwitcher': true,
		    numZoomLevels: 15,
		}),*/
		'osm': new OpenLayers.Layer.OSM ('OSM Base Layer'),
		'google_street': new OpenLayers.Layer.Google ('Google Base Layer', {
                    type: google.maps.MapTypeId.STREET
		}),
		'google_satellite': new OpenLayers.Layer.Google ('Google Base Layer', {
                    type: google.maps.MapTypeId.SATELLITE
		}),
	    }
	    
	    var current = null;

	    var checkOption = function (text, id, checked) {
		if (checked) {
		    current = baseLayers[id]
		    map.addLayer (current);
		}
		return {
		    'text': text,
		    checked: checked,
		    group: 'map_base',
		    checkHandler: function () {
			map.removeLayer (current);
			current = baseLayers[id];
			map.addLayer (current);
		    },
		 };
	     };

	     var menu = new Ext.menu.Menu ({
		 items: [
		     //checkOption ('None', 'none', false),
		     checkOption ('Open Street Map', 'osm', true),
		     checkOption ('Google Street Map', 'google_street', false),
		     checkOption ('Google Satellite Map', 'google_satellite', false),
		],
	    });

	    var config = {
		text: 'Base Layer',
		menu: menu,
	    };
	    
	    hs.map.BaseLayer.superclass.constructor.call (this, config);
	},
    }),
};