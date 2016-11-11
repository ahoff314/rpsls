# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import random
import endpoints
from protorpc import remote, messages

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    GameForms, UserForms, HistoryForm
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

HIGH_SCORES_REQUEST = endpoints.ResourceContainer(
                          number_of_results=messages.IntegerField(1),)


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

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Get an individual user's active / unfinished games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        games = Game.query(Game.user == user.key)
        games = games.filter(Game.game_over == False)
        if games.count() > 0:
            return GameForms(items=[game.to_form("{}'s unfinished games.".format(
                request.user_name)) for game in games])
        else:
            raise endpoints.NotFoundException('This user has no active games!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/cancel_game',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancel an active game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.end_game(won=False)
            game.key.delete()
            return StringMessage(
                message='Game {} has been cancelled.'.format(
                    request.urlsafe_game_key))
        elif game and game.game_over:
            return StringMessage(
                message='Game {} is already over.'.format(
                    request.urlsafe_game_key))
        else:
            raise endpoints.NotFoundException('Game does not exist.')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=HistoryForm,
                      path='game/{urlsafe_game_key}/record',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """User's specific game history with selection recap"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return HistoryForm(items=game.record)
        else:
            raise endpoints.NotFoundException('That game does not exist')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('See the game_over status below')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=HIGH_SCORES_REQUEST,
                      response_message=UserForms,
                      path='scores/high_scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """High scores in descending order based on all time wins"""
        users = User.query().fetch(limit=request.number_of_results)
        users = sorted(users, key=lambda x: x.wins, reverse=True)
        return UserForms(items=[user.to_form() for user in users])

    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """User rankings by win percentage"""
        users = User.query(User.total_games > 0).fetch()
        users = sorted(users, key=lambda x: x.percentage, reverse=True)
        return UserForms(items=[user.to_form() for user in users])

api = endpoints.api_server([RpslsApi])
