from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class CVE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cve_id = db.Column(db.String(32), unique=True, nullable=False)
    cve_json = db.Column(db.Text, nullable=False)  # Store the full CVE JSON as text

class PackageComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.String(128), unique=True, nullable=False)
    component_json = db.Column(db.Text, nullable=False)  # Store the full package/component JSON as text
