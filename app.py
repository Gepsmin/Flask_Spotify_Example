from flask import Flask, request, render_template, redirect
import pymongo
import requests
import helper_functions


spotify_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer "
}

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://base_user:base_user_password@cluster0.dbcb9.mongodb.net/first")
db = client.first
collection = db.users
client_id = "82ffff3f23534eedba167129f0ea8e31"


@app.route('/get_user_full_info/<user_name>', methods=["GET"])
def get_user(user_name):
    response = helper_functions.get_user(user_name, collection)
    return response


@app.route('/save_user/<user_name>/<token>', methods=["POST"])
def save_user(user_name, token):
    # diger bilgilerin ihtiyacina gore yeni parametreler eklenmeli
    response = helper_functions.save_user(user_name, token, collection)
    return response


@app.route('/user/<token>', methods=["GET", "POST"])
def found_user(token):
    if request.method == "POST":
        # ana sayfaya geri don
        return redirect("/")
    else:
        spotify_headers["Authorization"] = spotify_headers["Authorization"] + token
        spotify_response = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=1", headers=spotify_headers)
        # gelen datayi inceledikten sonra dogru infolari cekecegim
        last_song_info = spotify_response.json()
        # burdan gerekli infolari doldurup sergileyecek
        return render_template("show_result.html", data="aaaaa")


@app.route('/learn_user/<user_name>', methods=["GET", "POST"])
def learn_user(user_name):
    if request.method == "POST":
        # redirect_uri duzeltilecek
        token = "3"
        # response token icericek ama tam formatini bilmiyorum
        user_response = requests.post('http://127.0.0.1:5000//save_user/{}/{}'.format(user_name, token))

        return redirect('/user/{}'.format(token))

    return render_template('learn_user.html', data=user_name)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        response = requests.get('http://127.0.0.1:5000//get_user_full_info/{}'.format(request.form['user']))
        try:
            result = response.json()
            # token reusable olucak diye umit ediyorum
            # eger olmazsa usera request atmak yerine sadece spotify requesti aticaz
            token = result["spotify_token"]
            return redirect('/user/{}'.format(token))
        except:
            # boyle bir user yok o zaman user infolarini almaliyiz
            response = requests.get(
                'https://accounts.spotify.com/authorize?client_id=82ffff3f23534eedba167129f0ea8e31&response_type=code&redirec_uri=https%3A%2F%2Fw127.0.0.1:5000%2Flearn_user%2F{0}&scope=user-read-recently-played'.format(request.form['user']))

            return response.text

    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
