# -*- coding: utf-8 -*-

"""
    Deployment settings
    All settings which are typically edited for a deployment should be done here
    Deployers shouldn't typically need to edit any other files.
    NOTE FOR DEVELOPERS:
    /models/000_config.py is NOT in the BZR repository, as this file will be changed
    during deployments.
    To for changes to be committed to trunk, please also edit:
    deployment-templates/models/000_config.py
"""

# Remind admin to edit this file
FINISHED_EDITING_CONFIG_FILE = False # change to True after you finish editing this file
if not FINISHED_EDITING_CONFIG_FILE:
    raise HTTP(501, body="Please edit models/000_config.py first")

deployment_settings = s3base.S3Config(T)

# Database settings
deployment_settings.database.db_type = "sqlite"
deployment_settings.database.host = "localhost"
deployment_settings.database.port = None # use default
deployment_settings.database.database = "sahana"
deployment_settings.database.username = "sahana"
deployment_settings.database.password = "password"
deployment_settings.database.pool_size = 30

# Authentication settings
# This setting should be changed _before_ registering the 1st user
deployment_settings.auth.hmac_key = "akeytochange"
# These settings should be changed _after_ the 1st (admin) user is
# registered in order to secure the deployment
deployment_settings.auth.registration_requires_verification = False
deployment_settings.auth.registration_requires_approval = False
deployment_settings.auth.openid = False

# Base settings
# Set this to the Public URL of the instance
deployment_settings.base.public_url = "http://127.0.0.1:8000"

# Set this to True to switch to Debug mode
# Debug mode means that uncompressed CSS/JS files are loaded
# JS Debug messages are also available in the Console
# can also load an individual page in debug mode by appending URL with
# ?debug=1
deployment_settings.base.debug = False

# Switch to "False" in Production for a Performance gain
# (need to set to "True" again when Table definitions are changed)
deployment_settings.base.migrate = True

# Enable/disable pre-population of the database.
# Should be True on 1st_run to pre-populate the database
# - unless doing a manual DB migration
# Then set to False in Production (to save 1x DAL hit every page)
# NOTE: the web UI will not be accessible while the DB is empty,
# instead run:
#   python web2py.py -N -S eden -M
# to create the db structure, then exit and re-import the data.
deployment_settings.base.prepopulate = True

# Set this to True to use Content Delivery Networks to speed up Internet-facing sites
deployment_settings.base.cdn = False

# Email settings
# Outbound server
deployment_settings.mail.server = "127.0.0.1:25"
# Useful for Windows Laptops:
#deployment_settings.mail.server = "smtp.gmail.com:587"
#deployment_settings.mail.login = "username:password"
# From Address
deployment_settings.mail.sender = "'Sahana' <sahana@your.org>"
# Address to which mails get sent to approve new users
deployment_settings.mail.approver = "useradmin@your.org"

# Twitter settings:
# Register an app at http://twitter.com/apps
# (select Aplication Type: Client)
# You'll get your consumer_key and consumer_secret from Twitter
# You can keep these empty if you don't need Twitter integration
deployment_settings.twitter.oauth_consumer_key = ""
deployment_settings.twitter.oauth_consumer_secret = ""

# L10n settings
# Uncomment this if the deployment is just in a few countries
# (used in the GIS Location Selector)
#deployment_settings.L10n.countries = ["PK"]
#deployment_settings.L10n.default_country_code = 1
# Languages used in the deployment (used for Language Toolbar & GIS Locations)
# http://www.loc.gov/standards/iso639-2/php/code_list.php
deployment_settings.L10n.languages = {
    "en":T("English"),
    "el":T("Greek"),
    "es":T("Spanish"),
    #"fr":T("French"),
    #"pa":T("Punjabi"),
    #"ps":T("Pashto"),
    #"sd":T("Sindhi"),
    "ja":T("Japanese"),
    "ur":T("Urdu"),
    "zh-tw":T("Chinese (Taiwan)"),
}
# Default language for Language Toolbar (& GIS Locations in future)
deployment_settings.L10n.default_language = "en"
# Display the language toolbar
deployment_settings.L10n.display_toolbar = True
# Default timezone for users
deployment_settings.L10n.utc_offset = "UTC +0000"
# Religions used in Person Registry
# @ToDo: find a better code
# http://eden.sahanafoundation.org/ticket/594
deployment_settings.L10n.religions = {
    "none":T("none"),
    "christian":T("Christian"),
    "muslim":T("Muslim"),
    "jew":T("Jew"),
    "buddhist":T("Buddhist"),
    "hindu":T("Hindu"),
    "bahai":T("Bahai"),
    "other":T("other")
}

# GIS (Map) settings
# Provide a tool to select locations via a map on all forms with location_id
deployment_settings.gis.map_selector = True
# Display Resources recorded to Admin-Level Locations on the map
deployment_settings.gis.display_L0 = False
# Currently unused
#deployment_settings.gis.display_L1 = True
# Allow non-MapAdmins to edit Admin locations?
# (defaults to True, if not set)
deployment_settings.gis.edit_L0 = False
deployment_settings.gis.edit_L1 = True
#deployment_settings.gis.edit_L2 = True
deployment_settings.gis.locations_hierarchy = {
    "L0":T("Country"),
    "L1":T("Province"),
    "L2":T("District"),
    "L3":T("Town"),
    "L4":T("Village"),
    #"L5":T("Neighbourhood"),   # Currently not supported by testSuite
    "XX":T("Imported")          # Filtered from view as no detailed information & many duplicates (e.g. coming from Ushahidi)
}
# Should we require locations to follow strict hierarchy?
deployment_settings.gis.strict_hierarchy = False
# Maximum Marker Size
# (takes effect only on display)
deployment_settings.gis.marker_max_height = 35
deployment_settings.gis.marker_max_width = 30
# Duplicate Features so that they show wrapped across the Date Line?
# Points only for now
# lon<0 have a duplicate at lon+360
# lon>0 have a duplicate at lon-360
deployment_settings.gis.duplicate_features = False
# Mouse Position: 'normal', 'mgrs' or 'off'
deployment_settings.gis.mouse_position = "normal"
# Print Service URL: http://eden.sahanafoundation.org/wiki/BluePrintGISPrinting
#deployment_settings.gis.print_service = "/geoserver/pdf/"
# Do we have a spatial DB available? (currently unused. Will support PostGIS & Spatialite.)
deployment_settings.gis.spatialdb = False
# GeoServer (Currently used by GeoExplorer. Will allow REST control of GeoServer.)
# NB Needs to be publically-accessible URL for querying via client JS
#deployment_settings.gis.geoserver_url = "http://localhost/geoserver"
#deployment_settings.gis.geoserver_username = "admin"
#deployment_settings.gis.geoserver_password = "password"

# OpenStreetMap settings:
# Register your app by logging in to www.openstreetmap.org & then selecting 'oauth settings'
deployment_settings.osm.oauth_consumer_key = ""
deployment_settings.osm.oauth_consumer_secret = ""

# Security Policy settings
# Lock-down access to Map Editing
#deployment_settings.security.map = True
# Security Policy (defaults to 1 = Simple)
#deployment_settings.security.policy = 2 # Editor
# Should users be allowed to register themselves?
deployment_settings.security.self_registration = True
# Use 'soft' deletes
deployment_settings.security.archive_not_delete = True
# Audit settings
# We Audit if either the Global or Module asks us to
# (ignore gracefully if module author hasn't implemented this)
# NB Auditing (especially Reads) slows system down & consumes diskspace
#deployment_settings.security.audit_write = False
#deployment_settings.security.audit_read = False

# UI/Workflow options
# Should user be prompted to save before navigating away?
#deployment_settings.ui.navigate_away_confirm = False
# Should potentially large dropdowns be turned into autocompletes?
# (unused currently)
#deployment_settings.ui.autocomplete = True

# Comment/uncomment modules here to disable/enable them
# Modules menu is defined in 01_menu.py
from gluon.storage import Storage
from gluon.contrib.simplejson.ordered_dict import OrderedDict
deployment_settings.modules = OrderedDict(
    default = Storage(
            name_nice = T("Home"),
            restricted = False, # Use ACLs to control access to this module (currently deactivated)
            access = None,      # All Users (inc Anonymous) can see this module in the default menu & access the controller
            module_type = 0     # This item is always 1st in the menu
        ),
    admin = Storage(
            name_nice = T("Administration"),
            description = T("Site Administration"),
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
            module_type = 0     # This item is handled separately in the menu
        ),
    gis = Storage(
            name_nice = T("Map"),
            description = T("Situation Awareness & Geospatial Analysis"),
            restricted = False,
            module_type = 1,     # 1st item in the menu
            resources = Storage(
                gis_location = {"importer" : True}
             )
        ),
    doc = Storage(
            name_nice = T("Documents and Photos"),
            description = T("A library of digital resources, such as photos, documents and reports"),
            restricted = False,
            module_type = 10,
        ),
    msg = Storage(
            name_nice = T("Messaging"),
            description = T("Sends & Receives Alerts via Email & SMS"),
            restricted = False,
            module_type = 10,
        ),
    pr = Storage(
            name_nice = T("Person Registry"),
            description = T("Central point to record details on People"),
            restricted = False,
            access = "|1|",     # Only Administrators can see this module in the default menu (access to controller is possible to all still)
            module_type = 10,
            resources = Storage(
                pr_address = {"importer" : True},
                pr_pe_contact = {"importer" : True},
                pr_presence = {"importer" : True},
                pr_identity = {"importer" : True},
                pr_person = {"importer" : True},
                pr_group = {"importer" : True},
                pr_group_membership = {"importer" : True},
            )
        ),
    pf = Storage(
            name_nice = T("Person Finder"),
            description = T("Helps to report and search for Missing Persons"),
            restricted = False,
            module_type = 10,
        ),
    dvi = Storage(
            name_nice = T("Disaster Victim Identification"),
            description = T("Disaster Victim Identification"),
            restricted = True,
            module_type = 10,
            #access = "|DVI|",      # Only users with the DVI role can see this module in the default menu & access the controller
            #audit_read = True,     # Can enable Audit for just an individual module here
            #audit_write = True,
            resources = Storage(
                dvi_recreq = {"importer" : True},
            )
        ),
    #dvr = Storage(
    #        name_nice = T("Disaster Victim Registry"),
    #        description = T("Traces internally displaced people (IDPs) and their needs"),
    #        module_type = 10
    #    ),
    org = Storage(
            name_nice = T("Organization Registry"),
            description = T('Lists "who is doing what & where". Allows relief agencies to coordinate their activities'),
            restricted = False,
            module_type = 10,
            resources = Storage(
                org_organisation = {"importer" : True},
                org_office = {"importer" : True},
                org_staff = {"importer" : True}
            )
        ),
    project = Storage(
            name_nice = T("Project Tracking"),
            description = T("Tracking of Projects, Activities and Tasks"),
            restricted = False,
            module_type = 10
        ),
    # NB Budget module depends on Project Tracking Module
    budget = Storage(
            name_nice = T("Budgeting Module"),
            description = T("Allows a Budget to be drawn up"),
            restricted = False,
            module_type = 10,
            resources = Storage(
                budget_item = {"importer" : True},
                budget_kit = {"importer" : True},
                budget_bundle = {"importer" : True},
            )
        ),
    logs = Storage(
            name_nice = T("Logistics Management"),
            description = T("Managing, Storing and Distributing Items"),
            restricted = False,
            module_type = 10
        ),
    # NB RMS module depends on HMS, CR & Project
    rms = Storage(
            name_nice = T("Requests"),
            description = T("Tracks requests for aid and matches them against donors who have pledged aid"),
            restricted = False,
            module_type = 3,
            resources = Storage(
                rms_req = {"importer" : True},
            )
        ),
    cr = Storage(
            name_nice = T("Shelter Registry"),
            description = T("Tracks the location, distibution, capacity and breakdown of victims in Shelters"),
            restricted = False,
            module_type = 10,
            resources = Storage(
                cr_shelter = {"importer" : True }
            )
        ),
    hms = Storage(
            name_nice = T("Hospitals"),
            description = T("Helps to monitor status of hospitals"),
            restricted = False,
            module_type = 10,
            resources = Storage(
                hms_hospital = {"importer" : True}
            )
        ),
    vol = Storage(
            name_nice = T("Volunteers"),
            description = T("Manage volunteers by capturing their skills, availability and allocation"),
            restricted = False,
            module_type = 10,
        ),
    irs = Storage(
            name_nice = T("Incident Reporting"),
            description = T("Incident Reporting System"),
            restricted = False,
            module_type = 10
        ),
    # Assess currently depends on IRS
    assess = Storage(
            name_nice = "Assessments",
            description = "Rapid Assessments & Flexible Impact Assessments",
            restricted = False,
            module_type = 2,
        ),
    survey = Storage(
            name_nice = "Survey Module",
            description = "Create, enter, and manage surveys.",
            restricted = False,
            module_type = 10,
        ),
    delphi = Storage(
            name_nice = T("Delphi Decision Maker"),
            description = T("Supports the decision making of large groups of Crisis Management Experts by helping the groups create ranked list."),
            restricted = False,
            module_type = 10,
        ),
    importer = Storage(
            name_nice = "Spreadsheet Importer",
            description = "Used to import data from spreadsheets into the database",
            restricted = False,
            module_type = 10,
        ),
    #flood = Storage(
            #name_nice = T("Flood Alerts"),
            #description = T("Flood Alerts show water levels in various parts of the country"),
            #restricted = False,
            #module_type = 10
        #),
    #ticket = Storage(
            #name_nice = T("Ticketing Module"),
            #description = T("Master Message Log to process incoming reports & requests"),
            #restricted = False,
            #module_type = 10,
        #),
    #lms = Storage(
            #name_nice = T("Logistics Management System"),
            #description = T("An intake system, a warehouse management system, commodity tracking, supply chain management, procurement and other asset and resource management capabilities."),
            #restricted = False,
            #module_type = 10
        #),
)
