import flask
from flask import request, jsonify

from redditmends_bot import RedditmendsBot
from redditmends_bot import CommentQueryMethod

app = flask.Flask(__name__)
app.config["DEBUG"] = True

bot = RedditmendsBot("redditmends_bot")

@app.route('/', methods=['GET'])
def home():
    return "<h1>Redditmends</h1>"

@app.route('/api/recommendations', methods=['GET'])
def recommendations():
    if 'term' in request.args:
        term = request.args['term']
    else:
        return "Error: No term field provided. Please specify an id."

    bot.run(search_term = term, comment_query_method = CommentQueryMethod.PRAW, num_top_recommendations = 5)
    return "<h1>Redditmends bot</h1><p>{0}</p>".format(bot.result)