from report import r_postbuy
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

@app.route("/")
def home():
        return "<h1>Api-Postbuy</h1>"

@app.route('/postbuy', methods=['GET','POST'])
def postbuy():
    if request.method == 'POST':
        
        datainput = request.json
        result = r_postbuy.postbuy(datainput)

        data = {
            'pesan': result,
            'advertiser' : 'm'
        }
        
        return make_response(jsonify({'data':data}),200)

if __name__ == "__main__":
    # app.run(host='0.0.0.0')
    app.run(host="0.0.0.0", debug=True)