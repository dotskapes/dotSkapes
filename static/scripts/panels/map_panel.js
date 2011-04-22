hs.map = {
    Panel: Ext.extend (Ext.Panel, {
	constructor: function (config) {
	    var mapPanel;
	    var thisPanel = this;
	    var layers = {};
	    if (!config)
		config = {};

	    this.addMap = function (node) {
		var map = mapPanel.getMap ();
		if (!(node.filename in layers)) {
		    /*layers[node.filename] = new OpenLayers.Layer.WMS (
			"Brazil",
			geoserver_url + '/wms',
			{
			    layers: node.filename,
			    transparent: true,
			    format: "image/png",
			    projection: 'EPSG:9000913',
			},
			{
			    isBaseLayer: false,
			    displayOutsideMaxExtent: true,
			}
		    );*/
		    console.log (node);
		    layers[node.filename] = new OpenLayers.Layer.Vector (null, {
			projection: 'EPSG:4326',
			strategies: [new OpenLayers.Strategy.Fixed()],
			protocol: new OpenLayers.Protocol.WFS.v1_1_0 ({
			    url: 'http://zk.healthscapes.org/geoserver/wfs',
			    featureType: node.filename,
			    featurePrefix: node.prefix,
			}),
		    });
		}
		map.addLayer (layers[node.filename]);
	    };

	    this.removeMap = function (node) {
		var map = mapPanel.getMap ();
		map.removeLayer (layers[node.filename]);
	    };

	    Ext.apply (config, {
		layout: 'border',
		listeners: {
		    render: function (e) {
			mapPanel = new hs.map.MapPanel ({
			    region: 'center',
			});
			thisPanel.add (mapPanel);
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
};