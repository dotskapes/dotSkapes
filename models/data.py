def load_user_globals ():
    output = attr_dict ()
    if check_logged_in ():
        output.update ({'side_bar': True, 'tool_list': dm.local_load ('tools').json (), 'tool_saved_results': dm.local_load ('results').json (), 'tool_saved_analyses': dm.local_load ('analyses').json (), 'maps_saved': dm.local_load ('maps').json ()})
        if check_role (dev_role):
            output.update ({'dev_tools': True, 'in_dev': dm.local_load ('dev_tools').json ()})
        else:
            output.update ({'dev_tools': False})
    else:
        output.update ({'side_bar': False, 'dev_tools': False})
    return output

def get_datatypes ():
    return dm.get_types ()
