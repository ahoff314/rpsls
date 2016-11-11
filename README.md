# ROCK PAPER SCISSORS LIZARD SPOCK

"Scissors cuts paper, paper covers rock, rock crushes lizard, lizard poisons Spock, Spock smashes scissors,
scissors decapitates lizard, lizard eats paper, paper disproves Spock, Spock vaporizes rock, and as it always has,
rock crushes scissors."      - Sheldon Cooper


## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
2.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
3.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.

## How To Play

Rock Paper Scissors Lizard Spock is very similar to the classic game of rock paper scissors. Select either Rock, Paper,
Scissors, Lizard, or Spock. The computer you are playing against will randomly choose one of these selections.

Scissors cuts paper
paper covers rock,
rock crushes lizard,
lizard poisons Spock,
Spock smashes scissors,
scissors decapitates lizard,
lizard eats paper,
paper disproves Spock,
Spock vaporizes rock,
and as it always has,
rock crushes scissors.

You can win, lose, or tie. Each result contributes to your overall record and high score.

Simple right? After creating a user and a new game, play a few games using the make_move endpoint and you'll get the
hang of it! Further instructions to test the endpoints and play a RPSLS game are below.

## Testing

1. Create a new user using the create_user endpoint
2. Create a new game using the new_game endpoint. Make sure to save the urlsafe_key for later use
3. Play RPSLS by using the make_move endpoint. Enter an applicable selection to play against the computer
4. Select the get_high_scores (all time wins) or get_user_rankings (win / loss ratio) to see user scores and results
5. Test a specific game history using get_game_history and the urlsafe_key parameter
6. The urlsafe_key can also be used to cancel a game or return the current game state

 
##Game Description:
Rock Paper Scissors Lizard Spock is a fun variant of the classic game we all know and love.
Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, selection
    - Returns: GameForm with new game state.
    - Description: Accepts a selection and play a RPSLS game against the computer
    
 - **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user
    - Returns: GameForms
    - Description: Returns all of a user's active games.
    
 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel_game'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage
    - Description: Cancel existing game.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/record'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: HistoryForm
    - Description: User's specific game history with selection recap.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: UserForms
    - Description: Returns the current game state

 - **get_high_scores**
    - Path: 'scores/high_scores'
    - Method: GET
    - Parameters: None
    - Returns: UserForms
    - Description: High scores in descending order based on all time wins.

 - **get_user_rankings**
    - Path: 'users/rankings'
    - Method: GET
    - Parameters: None
    - Returns: UserForms
    - Description: User rankings by win percentage.


##Forms Included:
 - **UserForm**
    - Representation of a User's state
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.