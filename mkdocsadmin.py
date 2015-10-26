# name:         mkdocsadmin.py
# description:  Flask based python project which is used as a backend for
#               editing markdown files used by the mkdocs static site generator
#               application. This enables it to be used in a basic wiki-like
#               manner without needing to edit the files on the server itself.

from flask import flash, Flask, redirect, render_template, request, \
                  url_for
from werkzeug.utils import secure_filename
from subprocess import CalledProcessError, check_call
from time import localtime, strftime
from sys import path as syspath
from yaml import dump, safe_load
import logging
import os

# user configurable value for modifying the admin URI
# this value should always start with a /
ADMINHOME = '/mkdadmin'

app = Flask(__name__, static_url_path=ADMINHOME + '/static')
app.config.from_object('mkadmconfig.Config')

logfilename = app.config['LOGFILE']

# build logger and its configuration to write script data to specified log
logger = logging.getLogger('mkadmlogger')
logger.setLevel(logging.INFO)
logformatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')
if logfilename != '':
    fh = logging.FileHandler(logfilename)
else:
    fh = logging.FileHandler(os.path.join(syspath[0], 'mkdocsadmin.log'))

fh.setFormatter(logformatter)
logger.addHandler(fh)


def build_docs():
    try:
        mkdbin = app.config['MKDOCS_BIN']
        mkdclean = app.config['MKDOCS_CLEAN']
        mkddir = app.config['MKDOCS_DIR']

        # move into mkdocs directory to ensure proper build path
        os.chdir(mkddir)

        # purge build html files before building to ensure only existing
        # documents are present
        if mkdclean:
            check_call([mkdbin, 'build', '--clean'])
        else:
            check_call([mkdbin, 'build'])

    except CalledProcessError:
        logger.error(CalledProcessError)
    except PermissionError:
        logger.error('Permission denied to binary or build path.')
        logger.error('Binary path is %s', mkdbin)
        logger.error('Build path is %s', mkddir)


def norm_docdir():
    """ Normalize path to match OS standards """
    return os.path.normpath(app.config['MKDOCS_DIR'])


def get_doclist():
    """ simple function to return a list of all located documents """

    mkddir = norm_docdir()

    docs = []
    for doc in os.listdir(os.path.join(mkddir, 'docs')):
        if '.md' in doc:
            docs.append(doc)
    return docs


@app.route(ADMINHOME)
def display_index():
    return render_template('layout.html', doclist=get_doclist())


@app.route(ADMINHOME + '/log')
def display_log():
    if logfilename != '':
        logfile = logfilename
    else:
        logfile = os.path.join(syspath[0], 'mkdocsadmin.log')

    logdata = ''

    # only show log data if the log file exists, else redirect to blank
    # index page and display an error
    try:
        with open(logfile, 'r') as inlogfile:
            logdata = inlogfile.read().splitlines()
    except FileExistsError:
        logger.error('%s does not exist', logfile)

        flash('Log file ' + logfile + ' not found. Skipping...')
        return redirect(url_for('display_index'))
    except PermissionError:
        logger.error('Permission denied to write to %s', logfile)

        flash('Permission denied for reading file ' + logfile)
        return redirect(url_for('display_index'))
    finally:
        return render_template('display_log.html', doclist=get_doclist(),
                               log_content=logdata)


@app.route(ADMINHOME + '/edit/<filename>')
def display_edit(filename):

    mkddir = norm_docdir()

    safe_filename = os.path.join(mkddir, 'docs', filename)
    content = ''
    try:
        with open(safe_filename, 'r') as editfile:
            content = editfile.read()
        return render_template('edit_doc.html', doclist=get_doclist(),
                               filename=filename, content=content)
    except FileExistsError:
        logger.error('File %s does not exist. No changes have been made.',
                     safe_filename)

        flash('File not found at path ' + safe_filename)
        return redirect(url_for('display_index'))


@app.route(ADMINHOME + '/edit/<filename>', methods=['POST'])
def submit_edit(filename):

    mkddir = norm_docdir()

    safe_filename = os.path.join(mkddir, 'docs', filename)
    try:
        with open(safe_filename, 'w') as editfile:
            for line in request.form['edit_content']:
                editfile.write(line.rstrip('\n'))
        logger.info('Edit for %s saved successfully.', safe_filename)

        build_docs()

        flash('File ' + filename + ' edits saved successfully!')
    except FileExistsError:
        logger.error('File %s not found. Edits not saved.', filename)
        flash('Error saving file ' + safe_filename +
              '. Please see the log for detail')
    except Permissionerror:
        logger.error('Permission denied to file %s. Edits not saved.',
                     safe_filename)
        flash('Error saving file ' + safe_filename +
              '. Please see the log for detail')
    finally:
        return redirect(url_for('display_edit', filename=filename))


@app.route(ADMINHOME + '/new')
def display_new():
    return render_template('new_doc.html', doclist=get_doclist())


@app.route(ADMINHOME + '/new', methods=['POST'])
def submit_new():
    """ method to create the new markdown file and append it to the mkdocs
        config file to display as a page """

    mkddir = norm_docdir()

    # ensure filename is safe for the filesystem, string any extension from
    # user input, and append markdown file extenstion for mkdocs validity
    safe_filename = secure_filename(request.form['in_filename'])
    if '.' in safe_filename:
        safe_filename = safe_filename.split('.')[0] + '.md'
    else:
        safe_filename = safe_filename + '.md'

    try:
        doc = os.path.join(mkddir, 'docs', safe_filename)

        # only create new file if it does not already exist or log exception
        if not os.path.exists(doc):
            with open(doc, 'w') as newfile:
                for line in request.form['in_content']:
                    newfile.write(line.strip('\n'))
            logger.info('File %s successfully created.', doc)
        else:
            raise FileExistsError

    except FileExistsError:
        logger.error('%s already exists. Skipping.', doc)
    except PermissionError:
        logger.error('Permission denied to document path. '
                     'Please verify permissions and retry.')

    try:
        confdata = {}
        mkdconfig = os.path.join(mkddir, 'mkdocs.yml')

        # read in mkdocs.yml from docs directory and parse the yaml data into
        # a dictionary to ensure formatting is correct
        with open(mkdconfig, 'r') as conffile:
            # use yaml.safe_load function to ensure config dictionary is built
            confdata = safe_load(conffile)

            # set pagename to filename without extension
            pagename = safe_filename.split('.')[0]

        with open(mkdconfig, 'w') as conffile:
            # if new document directory is created generate a default page
            if 'pages' not in confdata.keys():
                confdata['pages'] = [{'home': 'index.md'}]

            # add the new page title and filename to the pages list
            # this ensures it is properly visible on the site
            confdata['pages'].append({pagename: safe_filename})

            dump(confdata, conffile)

    except FileExistsError:
        logger.error('mkdocs.yml not found in %s', mkddir)
    except PermissionError:
        logger.error('Permission denied to mkdocs.yml, unable to add page.')

    build_docs()

    flash('File ' + safe_filename + ' added successfully!')
    return redirect(url_for('display_edit', filename=safe_filename))


@app.route(ADMINHOME + '/status')
def display_filestatus():
    """ Get statistic data for this application and mkdocs files. """

    # remove index file as information is only needed for user created files
    docs = get_doclist()
    docs.remove('index.md')

    docdata = {}
    mkddir = norm_docdir()

    # for each markdown file build a dictionary using its name, path, path of
    # converted htmlfile and time the html was built
    for doc in docs:
        try:
            htmlpath = os.path.join(mkddir, 'site', doc.replace('.md', ''),
                                    'index.html')
            mdpath = os.path.join(mkddir, 'docs', doc)
            buildtime = strftime('%Y-%m-%d %H:%M:%S',
                                 localtime(os.path.getmtime(htmlpath)))

            docdata[doc] = {'name': doc,
                            'mdpath': mdpath,
                            'htmlpath':  htmlpath,
                            'buildtime': buildtime}
        except:
            pass

    return render_template('status.html', doclist=get_doclist(), data=docdata)


if __name__ == '__main__':
    host = app.config['HOST']
    port = app.config['PORT']

    app.run(host, port, debug=True)
