"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

# User class, this will not change
class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    wins = ndb.IntegerProperty(default=0)
    total_games = ndb.IntegerProperty(default=0)

    @property
    def percentage(self):
        """ Win percentage"""
        if self.total_games > 0:
            return float(self.wins)/float(self.total_games)
        else:
            return 0

    def to_form(self):
        """Returns a UserForm representation of User"""
        form = UserForm()
        form.user_name = self.name
        form.email = self.email
        form.wins = self.wins
        form.total_games = self.total_games
        form.percentage = self.percentage
        return form

    def win(self):
        """Adds win to User"""
        self.wins += 1
        self.total_games += 1
        self.put()

    def loss(self):
        """Adds loss to User"""
        self.total_games += 1
        self.put()


class Game(ndb.Model):
    """Game object"""
    attempts_remaining = ndb.IntegerProperty(required=True, default=5)
    user = ndb.KeyProperty(required=True, kind='User')
    record = ndb.StringProperty(repeated=True)

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new RPSLS game"""
        game = Game(user=user, game_over=False, record=[])
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.game_over = self.game_over
        form.message = message
        return form

    # TODO: Implement proper scoring
    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    game = ndb.StringProperty(required=true)
    message = ndb.StringProperty(required=true)
    user_selection = ndb.StringProperty(required=true)
    computer_selection = ndb.StringProperty(required=true)
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)

    # TODO: Update score form based on end game scoring
    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), guesses=self.guesses)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    min = messages.IntegerField(2, default=1)
    max = messages.IntegerField(3, default=10)
    attempts = messages.IntegerField(4, default=5)

# TODO: Update make a move form to work with game scoring
class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    selection = messages.StringField(1, required=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    user_selection = messages.StringField(4, required=True)
    computer_selection = messages.StringField(5, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """UserForm for outbound User information"""
    user_name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    total_games = messages.IntegerField(4, required=True)
    percentage = messages.FloatField(5, required=True)


class UserForms(messages.Message):
    """Return multiple UserForms"""
    items = messages.MessageField(UserForm, 1, repeated=True)


class RecordForm(messages.Message):
    """RecordForm for outbound Record information"""
    items = messages.StringField(1, repeated=True)
