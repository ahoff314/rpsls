# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import random
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForm, ScoreForms, GameForms, UserForm, UserForms, RecordForm
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))


@endpoints.api(name='rpsls', version='v1')
class RpslsApi(remote.Service):
    """ Rock Paper Scissors Lizard Spock | ahoff314 """
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a new User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A user with that name already exists!!!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!!!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates a new RPSLS game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A user with that name does not exist!')

        game = Game.new_game(user.key)

        return game.to_form('Rock! Paper! Scissors! Lizard! Spock!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Make your selection please.')
        else:
            raise endpoints.NotFoundException('Game not found!')


    # TODO: Meat and potatoes of game in make move endpoint
    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over.')

        selections = ['rock', 'paper', 'scissors', 'lizard', 'spock']
        if request.selection.lower() not in selections:
            raise endpoints.BadRequestException('Please choose rock, paper, scissors, lizard, or spock!')

        user_selection = request.selection.lower()
        computer_selection = random.choice(selections)
        msg = 'User plays ' + user_selection + '. Computer plays ' + computer_selection + '. '

        #
        if user_selection == computer_selection:
            result = 'tie'
        elif user_selection == 'rock':
            if (computer_selection == 'scissors') or (computer_selection == 'lizard'):
                result = 'user'
            else:
                result = 'computer'
        elif user_selection == 'paper':
            if (computer_selection == 'rock') or (computer_selection == 'spock'):
                result = 'user'
            else:
                result = 'computer'
        elif user_selection == 'scissors':
            if (computer_selection == 'paper') or (computer_selection == 'lizard'):
                result = 'user'
            else:
                result = 'computer'
        elif user_selection == 'lizard':
            if (computer_selection == 'spock') or (computer_selection == 'paper'):
                result = 'user'
            else:
                result = 'computer'
        elif user_selection == 'spock':
            if (computer_selection == 'rock') or (computer_selection == 'scissors'):
                result = 'user'
            else:
                result = 'computer'

        if result == 'user':
            message = msg + 'You win!'
            game.record.append(message)
            game.put()
            game.end_game(game=request.urlsafe_game_key, message=message,
                          user_selection=user_selection, computer_selection=computer_selection,
                          won=True)
            return game.to_form(message)
        elif result == 'computer':
            message = msg + 'You lose!'
            game.record.append(message)
            game.put()
            game.end_game(game=request.urlsafe_game_key, message=message,
                          user_selection=user_selection, computer_selection=computer_selection,
                          won=False)
            return game.to_form(message)
        elif result == 'tie':
            message = msg + 'Tie! Play RPSLS again.'
            game.record.append(message)
            game.put()
            game.end_game(game=request.urlsafe_game_key, message=message,
                          user_selection=user_selection, computer_selection=computer_selection,
                          won=False)
            return game.to_form(message)



    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return Leaderboard"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request): #TODO: get user scores
        """Returns all of an individual user's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A user with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    #TODO: Cancel game, get percentages, user rankings, records
api = endpoints.api_server([RpslsApi])
