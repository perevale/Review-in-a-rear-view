from imdb import IMDb
from flask import Flask, render_template, request, Response
from flask_restplus import Api, Resource
import requests
import json
from time import time
import sqlite3

dict_key = '27f7ff07-147b-4a26-a4ea-f97c5d5f0198'
base = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}'
API_URL = 'https://tinycards.duolingo.com/api/1/'
identifier = 'perevale'
password = 'beatriche123'
db_name = 'movie_vocab.sqlite'

app = Flask(__name__)
swagger = Api(app=app,
              version="1.0",
              title="Review in a Rear View",
              description="Learn English by watching movies!")


"""Define namespace"""
movies_name_space = swagger.namespace("movies", description='Get info about movies')
ia = IMDb()


@movies_name_space.route("/search_movie_by_name/<string:name>")  # Define the route
class MoviesListByName(Resource):
    @swagger.doc(responses={200: 'OK', 400: "No such movie found!"},
                 description="Get list of all movies with a given name")  # Documentation of route
    def get(self, name):
        movies = ia.search_movie(name)
        if len(movies) == 0:
            movies_name_space.abort(400, status="No such movie found!", statusCode="400")
        movies = [{'movieID': i.__dict__['movieID'], 'data': i.__dict__['data']} for i in movies]
        # movies = jsonify(movies)
        return movies


@movies_name_space.route("/<string:id>/search_movie_by_id")  # Define the route
class MovieByID(Resource):
    @swagger.doc(responses={200: 'OK', 400: "ID is not valid!"},
                 description="Get a movie with a given ID ")  # Documentation of route
    def get(self, id):
        movie = ia.get_movie(id).__dict__['data']
        if not movie:
            movies_name_space.abort(400, status="ID is not valid!", statusCode="400")
        movie = {'movieID': id, 'plot outline': movie['plot outline'], 'year': movie['year'], 'title': movie['title'],
                 'cover_url': movie['cover url'], 'rating': movie['rating']}
        return movie


vocab_name_space = swagger.namespace("vocabulary", description='Get definitions of words')


@vocab_name_space.route("/search_word/<string:word>")  # Define the route
class Definition(Resource):
    @swagger.doc(responses={200: 'OK'},
                 description="Get list of all definitions for a given word")  # Documentation of route
    def get(self, word):
        base_url = base.format(word, dict_key)
        response = json.loads(requests.get(base_url).content.decode('utf-8'))
        # j = 1
        defs = []
        for i in response:
            for desc in i['shortdef']:
                defs.append(desc)
                # print("({}) - {}".format(j, desc))
                # j += 1
        return defs


flashcards_name_space = swagger.namespace("flashcards", description='Operate with flashcards')


@flashcards_name_space.route("/login")  # Define the route
class Login(Resource):
    @swagger.doc(responses={200: 'OK'}, description="Get user id")  # Documentation of route
    def get(self):
        request_payload = {
            'identifier': identifier,
            'password': password
        }

        r = requests.post(url=API_URL + 'login', json=request_payload)
        json_response = r.json()

        set_cookie_headers = {
            k: v for (k, v) in
            [c.split('=') for c in r.headers['set-cookie'].split('; ')]
        }
        jwt = set_cookie_headers.get('jwt_token')

        user_id = json_response.get('id')
        return user_id, jwt


@flashcards_name_space.route("/get_decks")  # Define the route
class GetDecks(Resource):
    @swagger.doc(responses={200: 'OK'}, description="Get list of all the decks")  # Documentation of route
    def get(self):
        user_id, jwt = Login().get()
        request_url = API_URL + 'decks?userId=' + str(user_id)
        r = requests.get(request_url, cookies={'jwt_token': jwt})
        decks = json.loads(r.content.decode('utf-8'))['decks']
        decks = [{'id': deck['id'], 'name': deck['name']} for deck in decks]
        return decks


@flashcards_name_space.route("/get_deck/<string:deck_id>")  # Define the route
class GetDeck(Resource):
    @swagger.doc(responses={200: 'OK'}, description="Get list of all the decks")  # Documentation of route
    def get(self, deck_id):
        user_id, jwt = Login().get()
        request_url = API_URL + 'decks/' + deck_id
        request_url += '?expand=true'
        r = requests.get(url=request_url, cookies={'jwt_token': jwt})
        deck = json.loads(r.content.decode('utf-8'))
        return deck


@flashcards_name_space.route("/create_card/<string:deck_id>/<string:card_name>/<string:fact>")  # Define the route
class UpdateDeck(Resource):
    @swagger.doc(responses={200: 'OK'},
                 description="Create a card with a given name and a fact")  # Documentation of route
    def post(self, deck_id, card_name, fact):
        user_id, jwt = Login().get()

        deck = GetDeck().get(deck_id)

        side_front = {'concepts': [{'fact': {'type': 'TEXT', 'text': str(card_name)}}]}
        side_back = {'concepts': [{'fact': {'type': 'TEXT', 'text': str(fact)}}]}
        card = {'creationTimestamp': int(time()) * 1000, 'sides': [side_front, side_back]}
        deck['cards'].append(card)
        # deck['updatedAt'] = str(time())
        for k, v in deck.items():
            if isinstance(v, bool):
                deck[k] = str(v).lower()
            else:
                deck[k] = json.dumps(v)

        json_data = {
            'name': 'Test',  # deck['name'],
            'description': '',  # deck['description'],
            'private': deck['private'],
            'shareable': deck['shareable'],
            'cards': deck['cards'],
            'ttsLanguages': deck['ttsLanguages'],
            'blacklistedSideIndices': deck['blacklistedSideIndices'],
            'blacklistedQuestionTypes': deck['blacklistedQuestionTypes'],
            'gradingModes': deck['gradingModes'],
            'fromLanguage': 'en',
            'imageUrl': deck['imageUrl'],
            'coverImageUrl': deck['coverImageUrl'],
        }
        request_payload = json_data
        DEFAULT_HEADERS = {
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://tinycards.duolingo.com/',
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4)' +
                           ' AppleWebKit/537.36 (KHTML, like Gecko)' +
                           ' Chrome/58.0.3029.94 Safari/537.36')
        }
        headers = dict(DEFAULT_HEADERS)
        request_payload = json.dumps(request_payload)
        headers['Content-Type'] = 'application/json'
        r = requests.patch(url=API_URL + 'decks/' + deck_id,
                           data=request_payload, headers=headers,
                           cookies={'jwt_token': jwt})

        json_data = json.loads(r.content.decode('utf-8'))
        return json_data


database_name_space = swagger.namespace("database", description='Operate the data in the database')


@database_name_space.route("/update_database/<string:row>/")  # Define the route
class UpdateDatabase(Resource):
    @swagger.doc(responses={200: 'OK'}, description="Create a new definition")  # Documentation of route
    def post(self, row):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        # data = json.loads(json_row)
        movieID = row['MovieID']
        word = row['Word']
        desc = row['Description']

        print(movieID, word, desc)

        cur.execute('''CREATE TABLE IF NOT EXISTS MovieVocabulary (MovieID TEXT, Word TEXT, Description TEXT)''')
        cur.execute('SELECT Word, Description FROM MovieVocabulary WHERE MovieID = ? AND Word = ?', (movieID, word,))
        row = cur.fetchone()
        return_value = 'OK'
        if row is None:
            cur.execute('''INSERT INTO MovieVocabulary (MovieID, Word, Description) VALUES (?,?,?)''',
                        (movieID, word, desc))
        else:
            print("Record already found. No update made.")
            return_value = 'Record already exists'
        conn.commit()
        conn.close()
        return return_value

@database_name_space.route("/get_words_for_movie_id/<string:movieID>/")  # Define the route
class GetWordsFromDatabase(Resource):
    @swagger.doc(responses={200: 'OK'}, description="Create a new definition")  # Documentation of route
    def get(self, movieID):
        conn = sqlite3.connect(db_name)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        result = []
        cur.execute('''CREATE TABLE IF NOT EXISTS MovieVocabulary (MovieID TEXT, Word TEXT, Description TEXT)''')
        cur.execute('SELECT Word, Description FROM MovieVocabulary WHERE MovieID = ?', (movieID,))
        # row = cur.fetchall()
        for r in cur.fetchall():
            result.append(dict(r))
        conn.commit()
        conn.close()
        return result


@app.route("/home")
def home():
    return render_template('search.html')


@app.route("/search_movie_by_name")
def search_movie_by_name():
    name = request.args.get('name', '', type=str)
    movies = MoviesListByName().get(name)
    print()
    return render_template("list.html", title='List',
                           movies=movies)


@app.route("/movie", methods=['GET', 'POST'])
def movie_info():
    id = request.args.get('movieID', '', type=str)
    movie = MovieByID().get(id)
    db_words = GetWordsFromDatabase().get(id)
    # vocab = Definition().get()

    return render_template("movie.html", title=movie['title'],
                           movie=movie, db_words=db_words)

@app.route("/add_to_dict", methods=['POST'])
def add_to_dict():
    if request.method == 'POST':
        word = request.form.get('word','',type=str)
        desc = request.form.get('desc', '',type=str)
        id = request.form.get('id', '',type=str)
        row = {"MovieID":id, "Word":word, "Description":desc}
        UpdateDatabase().post(row)
        # movie = MovieByID().get(id)
        # db_words = GetWordsFromDatabase().get(id)
        # return render_template("movie.html", title=movie['title'],
        #                        movie=movie, db_words=db_words)
        # return redirect('/movie?movieID=',id)

        return Response(status=200)

@app.route("/add_to_flashcards", methods=['POST'])
def add_to_flashcards():
    if request.method == 'POST':
        word = request.form.get('front', '', type=str)
        desc = request.form.get('back', '', type=str)
        deck_id = 'a098def9-32f4-4446-a91e-5cab8c7fb239'
        UpdateDeck().post(deck_id, word, desc)
        return Response(status=200)



if __name__ == '__main__':
    app.run()  # debug=True
