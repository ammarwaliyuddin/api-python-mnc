from report import r_postbuy
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

@app.route("/")
def home():
        return "<h1>api-servicesss</h1>"

@app.route('/postbuy', methods=['GET','POST'])
def postbuy():
    if request.method == 'POST':
        try :
            datainput = request.json
            result = r_postbuy.postbuy(datainput)

            data = {
                'status': result
            }
            
            return make_response(jsonify({'data':data}),200)
    
        except Exception as e:
            
            data = {
                'status': False
            }
            return make_response(jsonify({'data':data}),400)


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
    # app.run(debug=True)