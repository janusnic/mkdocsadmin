# mkdocsadmin #
Flask application written to manage content for the [mkdocs] static site generator.
The site serves as an admin page and uses simply HTML forms to edit the text which will be used by mkdocs to render your documentation site.

I built this to use mkdocs as a makeshift wiki originally but do plan on expanding this to manage multiple mkdocs sites.

### Requirements ###
Most recent version of Flask and mkdocs.

This was tested on CentOS 7 and Debian 8 running Python 3.4.3. As the main code is in Flask it should work with Python 2 but this is not guarenteed.

### Installation ###
Simply clone this repository to a directory of your choice.

If running behind a full webserver you can simply proxy to http://127.0.0.1:5000/mkdadmin for a basic setup.

UWSGI and a systemd service can also be used if desired.

### Usage ###
The site can be used behind a full webserver or by simply running the script manually. By default it will listen on port 5000 for localhost only. This is configurable in the provided configuration script.

Once running simply navigate to the specified host and port followed by /mkdadmin to see the index page. 

*Note: No authentication is provided by this script! It can be provided by any other means of your choosing such as BasicAuth with the web server. This means anyone with access to the URL will be able to edit your site content.

For both edit and new docs clicking the save button will automatically run the 'mkdocs build' command on the server and generate the documentation. This will be immediately visible on the page configured for your site.

### Limitations ###
Currently this manages only a single site and is configured within the mkadmconfig.py file. You can change this at anytime and simply reload the script to work with the new directory.

Very basic UI. Some pages such as the log will simply scroll to fit the content. Additionally this will happen with large numbers of files.

Subpages are not supported. Nesting pages is not yet implemented. For best results I recommend setting the readthedocs theme within your mkdocs configuration file.

### Troubleshooting / Bug reporting ###
Please create any bug reports on this project's GitHub page with as much information as possible.

I did attempt to include as much logging as possible so when filing a bug report please include a copy of the error and log entry if possible. There may be some missing logging. If your error is not caught simply enable debug mode and provide the Python trace information.

[1]: http://www.mkdocs.org/ "mkdocs.org"