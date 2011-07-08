hs = {
    geoserver: {
	describe: function (map) {
	    return '/{{= request.application }}/geodata/describe_tmp?id=' + map.id;
	    //return map.src + '/wfs?request=DescribeFeatureType&typename=' + map.prefix + ':' + map.filename + '&version=1.1.0';
	}
    },
    user: {
	admin: {{if admin_role: }}true{{else:}}false{{pass}},
	dev: {{if dev_role: }}true{{else:}}false{{pass}},
    },
    application: '{{= request.application }}',
    url: function (controller, func, args, params) {
	if (!args)
	    args = [];

	var pstring = '';
	var p_spacer = '';
	if (params) {
	    p_spacer  = '?';
	    var plist = [];
	    for (key in params) {
		plist.push (key + '=' + encodeURIComponent (params[key]));
	    }
	    pstring = plist.join ('&');
	}

	var spacer = ''
	if (args.length > 0)
	    spacer = '/';
	return '/' + hs.application + '/' + controller + '/' + func + spacer + args.join ('/') + p_spacer + pstring;
    },
};