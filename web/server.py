from flask import Flask, render_template
# from markupsafe import escape


# app = Flask(__name__,
#             static_url_path='',
#             static_folder='templates',
#            )


# from flask import Flask
app = Flask(__name__,  static_url_path='/static', static_folder='templates')

# @app.route('/')
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path): #type:ignore
    return render_template('index.html', path=path)

if __name__ == '__main__':
    app.run()