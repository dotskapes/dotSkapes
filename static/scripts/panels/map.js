hs.map = {
    Panel: Ext.extend (Ext.Panel, {
	constructor: function (config) {
	    var mapPanel;
	    var thisPanel = this;
	    var layers = {};
	    var select = {};
	    var control = {};
	    if (!config)
		config = {};

	    this.addMap = function (node) {
		var map = mapPanel.getMap ();
		if (!(node.filename in layers)) {
		    layers[node.filename] = new OpenLayers.Layer.WMS (
			"Map",
			geoserver_url + '/ows',
			{
			    layers: node.prefix + ':' + node.filename,
			    transparent: true,
			    format: "image/png",
			    projection: 'EPSG:9000913',
			},
			{
			    srsName: 'EPSG:900913',
			    isBaseLayer: false,
			    displayOutsideMaxExtent: true,
			}
		    );
		    select[node.filename] = new OpenLayers.Layer.Vector("Selection", {styleMap: 
									   new OpenLayers.Style(OpenLayers.Feature.Vector.style["select"])
									  });
		    control[node.filename] = new OpenLayers.Control.GetFeature({
			protocol: OpenLayers.Protocol.WFS.fromWMSLayer(layers[node.filename], {
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
			toggleKey: "ctrlKey"
		    });

		    control[node.filename].events.register("featureselected", this, function(e) {
			select[node.filename].addFeatures([e.feature]);
		    });
		    control[node.filename].events.register("featureunselected", this, function(e) {
			select[node.filename].removeFeatures([e.feature]);
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
		    });*/
		}
		control[node.filename].activate ();
		map.addLayer (layers[node.filename]);
		map.addLayer (select[node.filename]);

	    };

	    this.removeMap = function (node) {
		var map = mapPanel.getMap ();
		map.removeLayer (layers[node.filename]);
		map.removeLayer (select[node.filename]);
		control[node.filename].deactivate ();
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