hs.map = {
    Panel: Ext.extend (Ext.Panel, {
	constructor: function (config) {
	    var mapPanel;
	    var toolbar;
	    var attrPanel;
	    var thisPanel = this;
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

	    this.addMap = function (node) {
		var map = mapPanel.getMap ();
		if (!(node.filename in layers)) {
		    layers[node.filename] = new OpenLayers.Layer.WMS (
			"Map",
			//geoserver_url + '/ows',
			'/' + hs.application + '/geoserver/wms',
			{
			    ID: node.id,
			    layers: node.prefix + ':' + node.filename,
			    transparent: true,
			    format: "image/png",
			    projection: 'EPSG:9000913',
			    //sld: 'http://zk.healthscapes.org/healthscapes/static/test.xsd',
			    styles: null,
			},
			{
			    isBaseLayer: false,
			    displayOutsideMaxExtent: true,
			}
		    );

		    control[node.filename] = new OpenLayers.Control.GetFeature({
			protocol: OpenLayers.Protocol.WFS.fromWMSLayer(layers[node.filename], {
			    ID: node.id,
			    srsName: 'EPSG:900913',
			}),
			/*protocol: new OpenLayers.Protocol.WFS.v1_1_0 ({
			    url: geoserver_url + '/ows',
			    featureType: node.filename,
			    featureNS: node.prefix,
			    srsName: 'EPSG:900913',
			}),*/
			box: true,
			hover: false,
			multipleKey: "shiftKey",
			toggleKey: "shiftKey"
		    });

		    control[node.filename].events.register("featureselected", this, function(e) {
			selectLayer.addFeatures([e.feature]);
		    });
		    control[node.filename].events.register("featureunselected", this, function(e) {
			selectLayer.removeFeatures([e.feature]);
		    });

		    map.addControl (control[node.filename]);

		    /*layers[node.filename] = new OpenLayers.Layer.Vector (null, {
			projection: 'EPSG:4326',
			strategies: [new OpenLayers.Strategy.Fixed()],
			protocol: new OpenLayers.Protocol.WFS.v1_1_0 ({
			    url: 'http://zk.healthscapes.org/geoserver/wfs',
			    featureType: node.filename,
			    featurePrefix: node.prefix,
			}),
			styleMap: defaultStyle,
		    });*/
		}
		selectControl = control[node.filename];
		//control[node.filename].activate ();
		map.addLayer (layers[node.filename]);
		//map.addLayer (select[node.filename]);
		attrPanel.loadMap (node);
	    };

	    this.removeMap = function (node) {
		var map = mapPanel.getMap ();
		map.removeLayer (layers[node.filename]);
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
						map.removeLayer (selectLayer);
						selectControl.deactivate ();
					    }
					},
				    },
				}),
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

	    var base = new OpenLayers.Layer.OSM ();
	    map.addLayer (base);

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

	    if (!config)
		config = {};

	    var setNewModel = function (data) {
		var cols = JSON.parse (data.responseText);
		var fields = []
		var colList = []
		for (var i = 0; i < cols.columns.length; i ++) {
		    colList.push (cols.columns[i]);
		    fields.push (cols.columns[i].header);
		}

		var colModel = new Ext.grid.ColumnModel ({
		    defaults: {
			sortable: true,
		    },
		    columns: colList,
		});

		var store = new Ext.data.JsonStore ({
		    root: 'features',
		    autoLoad: true,
		    fields: fields,
		    url: '/' + hs.application + '/geodata/read?id=' + cols.id,
		});
		thisPanel.reconfigure (store, colModel);
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
					id: current_map.id,
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
	    });
	    
	    hs.map.AttrPanel.superclass.constructor.call (this, config);
	},
    }),
};