hs.data = {
    fields: {
	{{ for datatype, model in data.iteritems (): }}
	{{= datatype }}: {
	    text: '{{= model.name }}',
	    fields: {
		id: {
		    visible: false,
		},
		tags: {
		    visible: true,
		    text: 'Tags',
		},
		{{ for field in model.public (): }}
		{{= field.name }}: {
		    {{ for k, v in field.display ().iteritems (): }}
		    {{ if type (v) == bool: }}
		    {{= k }}: {{= str(v).lower () }},
		    {{ elif type (v) == str: }}
		    {{= k }}: '{{= v }}',
		    {{ elif type (v) == int or type (v) == float: }}
		    {{= k }}: {{= v }},
		    {{ pass }}
		    {{ pass }}
		},
		{{ pass }}
	    },
	},
	{{ pass }}
    },
};
