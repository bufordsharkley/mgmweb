import flask
 
app = flask.Flask(__name__)

#Set application.debug=true to enable tracebacks on Beanstalk log output. 
#Make sure to remove this line before deploying to production.
app.debug=True
 
@app.route('/')
def hello_world():
    return "Hello world, running as package!"
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
