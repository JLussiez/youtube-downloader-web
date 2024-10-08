# -*- coding: utf-8 -*-
"""
The flask application package.
"""

from flask import Flask

app = Flask(__name__)

# Importation des vues pour enregistrer les routes
import python1.views
