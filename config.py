from dotenv import load_dotenv

import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, 'config.env'))

TOKEN = os.environ.get('TOKEN')
GROUP_ID = os.environ.get('GROUP_ID')
