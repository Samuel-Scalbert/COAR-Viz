from app.app import app
from flask import url_for as flask_url_for

# 🔧 Force every url_for() to include /software prefix
def prefixed_url_for(endpoint, **values):
    url = flask_url_for(endpoint, **values)
    # avoid double prefix if already has /software
    if not url.startswith('/software'):
        url = '/software' + url
    return url

# Apply globally in Jinja templates
app.jinja_env.globals['url_for'] = prefixed_url_for

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8040)

