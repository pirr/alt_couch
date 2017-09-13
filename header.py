import os
import re
import sys
import cherrypy
import jinja2
import hashlib
import subprocess
import couchdb
import json
import copy

import alt.cfg
from alt.dict_ import dict_

import vb.couch

import vb.script
# script = vb.script.Script()

# import install