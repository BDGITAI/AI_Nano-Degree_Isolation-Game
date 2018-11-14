"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import random
from isolation import Board
import itertools
import math
from random import randint

## MyPlayer is to be understood as the AI player the implementation in game_agent

class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """

def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    This should be the best heuristic function for your project submission.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
       
    #If game is lost then return minimal utility from MyPlayer point of view 
    if game.is_loser(player):
        return float("-inf")

    #If move leads to victory maximise utility from MyPlayer point of view 
    if game.is_winner(player):
        return float("inf")    
        
    #if beginning of the game MyPlayer will try to get in the center to have more opportunities in the future
    #Myplayer can be 1st player move_count =1 or 2nd player move_count=2
    if (game.move_count == 1 or game.move_count == 2):
        x,y = game.get_player_location(player)
        distance_to_center=float(((y-(game.height/2))**2+(x-(game.width/2))**2))
        #MyPlayer needs to be as close as possible to center. The minimum value is best
        #hence use negative value to center
        return float(-(distance_to_center))
 
    #if possible try to mirror the oponents move
    #symmetric_move will return inf if true or the distance to the symmetric move if not
    if symmetric_move(game, player) == float("inf"):
        return float("inf")
    else:
        #if cannot play symmetric move chose the move that give the more moves than the opponent
        number_player_move = float(len(game.get_legal_moves(player)))
        number_opponent_move = float(len(game.get_legal_moves(game.get_opponent(player))))       
        return (number_player_move-number_opponent_move)

def custom_score_2(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    ## Heuristic based on mirroring the moves of the oponent
    #If game is lost then return minimal utility from MyPlayer point of view 
    if game.is_loser(player):
        return float("-inf")

    #If move leads to victory maximise utility from MyPlayer point of view 
    if game.is_winner(player):
        return float("inf")   
    
    #try to play the most symmetric move. Mirroring move using center
    return symmetric_move(game, player)



def custom_score_3(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    #number of Myplayer moves
    own_moves = len(game.get_legal_moves(player))
    #number of opponent moves
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    #number of tiles that cannot be use anymore
    close_spaces = game.height * game.width - len(game.get_blank_spaces())

    #test win
    if player == game.inactive_player and opp_moves == 0:
        return float("inf")
    #test loss
    if player == game.active_player and own_moves == 0:
        return float("-inf")

    # ratio between opp moves and player moves. The smaller the better then return negative value
    # the more we progress in the game the more closed space we have
    # multiply by number of closed space to increase effect of having less moves than opponent towards
    # end of game
    # 0.5 added to avoid 0
    return -(opp_moves + 0.5) / (own_moves + 0.5) * close_spaces

def custom_score_3_before_submission(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    ## Heuristic based free tiles around the position
    ## As player moves as knight he can be at max 2 col or row from position in next turn
    ## Compute the number of occupied tiles 
    ## _|_|_|_|_
    ## _|_|_|_|_
    ## _|_|P|_|_
    ## _|_|_|_|_
    ## _|_|_|_|_
    
    #If game is lost then return minimal utility from MyPlayer point of view 
    if game.is_loser(player):
        return float("-inf")

    #If move leads to victory maximise utility from MyPlayer point of view 
    if game.is_winner(player):
        return float("inf")   
    
    #To ease computation create an extended board with a frame of 1s around it.
    #This allows using same computation when player in on the border of the board
    #and unreachable positions counts as 1s
    ## 1|1|1|1|1
    ## 1|1|1|1|1
    ## 1|1|P|_|_
    ## 1|1|_|_|_
    ## 1|1|_|_|_
    # create extended board already filled . 2 more rows on top and 2 more at bottom give 4. same for columns
    extended_board = [1]*((game.width+4)*(game.height+4))
    # now copy the game into the extended board
    # 1 are replaced with 0 if they are in empty in the game
    for i in range(0,game.height):
        for j in range(0,game.width):
            extended_board[(game.width+4)*(2+j)+2+i]=game._board_state[i+game.width*j]

    # create list of relative coordinates we want to use to compute occupation around a position
    # assume the position is at the center we need to move -2 to +2 in 2 directions    
    # first vector
    a = list(range(-2,3))
    # create diagonal positions (-2,-2),(-1,-1)....
    neighbours = list(zip(a,a))
    # using iter tools create missing combination
    neighbours += list(itertools.permutations(a,2))
    # now we have 25 relatives positions around the player location

    (x,y)=game.get_player_location(player)
    occupation = 0
    # sum all occupied tiles using relatives coordinates
    for n in neighbours:
        (r,c)=n
        #we want to favorise moves in empty places therefore the occupation is given as negative values
        #the more we have occupied tiles the worst it is
        # need to use offset to get correct position in extended board
        occupation -= extended_board[(2+game.width+2)*(2+y+r)+(2+x+c)]

    return float(occupation)

def symmetric_move(game, player):
    """Calculate the symmetric position of the player's opponent

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        inf if the player is symmetric to the opponent
        or
        distance of the player from the symmetric position of the oponent
    """    
    # player position
    (xp,yp) = game.get_player_location(player)
    #opponent position
    (xo,yo) = game.get_player_location(game.get_opponent(player))
    # board centre used a symmetry point
    xc = int(game.width/2)
    yc = int(game.height/2)
    # mirrored opponent position
    x1 = 2*xc - xo
    y1 = 2*yc - yo
    # if the player is in the mirrored position then return inf
    if (game.get_player_location(player))==(x1,y1):
        return float("inf")
    else:
        # return the distance from the mirrored position. The closer the better then 0 is the max value
        return -float((yp-y1)**2+(xp-x1)**2)

class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout


class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **************  YOU DO NOT NEED TO MODIFY THIS FUNCTION  *************

        For fixed-depth search, this function simply wraps the call to the
        minimax method, but this method provides a common interface for all
        Isolation agents, and you will replace it in the AlphaBetaPlayer with
        iterative deepening search.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        # to return a legal moves even in case of timeout
        possible_init_moves = game.get_legal_moves(self)
        if len(possible_init_moves) !=0:
            best_move = possible_init_moves[randint(0, len(possible_init_moves) - 1)]
        else:
            best_move = (-1, -1)
        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            move = self.minimax(game, self.search_depth)
            if(move != (-1, -1))and(move!=None):
                return move
            else:
                return best_move

        except SearchTimeout:
            return  best_move# Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth):
        """Implement depth-limited minimax search algorithm as described in
        the lectures.

        This should be a modified version of MINIMAX-DECISION in the AIMA text.
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        # monitor time left
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        # first call is MyPlayer turn, hence shall maximise the value 
        (move,utility) = self.maximise(game,depth,0)
        return move
        
    
    def terminal_test(self, game, current_depth, max_search_depth):
        """Test if the board is a terminal node or if it can be extended

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        current_depth : int
            current depth of the extended tree
            
        max_search_depth : int
            limit of the depth of the search tree
            
        Returns
        -------
        Boolean
            True if it is a terminal node
            False in other cases
        """        
        # can be a terminal node if
        # - reached the maximum depth of search
        # - no more legal moves
        # - or one player loses or win
        if len(game.get_legal_moves()) == 0 or game.utility(game.active_player) !=0 or current_depth>max_search_depth:
            return True
        else:
            False
    
    def maximise(self, game, max_search_depth,parent_depth):
        """maximise function on minimax algorithm

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        parent_depth : int
            depth of the node from where the function is called
            
        max_search_depth : int
            limit of the depth of the search tree
            
        Returns
        -------
        Boolean
            (move,float)
            return the max move with its utility value
        """ 
        # monitor time left
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        
        # update serach depth
        current_depth=parent_depth+1
        
        # check if node is a terminal node of the search tree
        if self.terminal_test(game,current_depth,max_search_depth):
            # if this is a terminal node then we evaluate the board
            res = self.score(game,game.active_player)
            return (None,res)
        
        # initialise move and utility value before search and recursive call
        (maxMove, maxUtility) = (None,-float("inf"))
    
        # if not a terminal node then we will test all possible children note
        # children node are here given by all possible legal moves for the active player
        for move in game.get_legal_moves():
            # create the children node associated to a move
            # WARNING : forecast return a new board where the active player is changed
            # the children node active player is the opponent
            child=game.forecast_move(move)
            # call the minimise function as per minimax
            (_,utility) = self.minimise(child,max_search_depth,current_depth)
            # maximise utility
            if utility > maxUtility:
                (maxMove, maxUtility) = (move,utility)
        
        return (maxMove, maxUtility)

    def minimise(self, game, max_search_depth,parent_depth):
        """minimise function on minimax algorithm

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        parent_depth : int
            depth of the node from where the function is called
            
        max_search_depth : int
            limit of the depth of the search tree
            
        Returns
        -------
        Boolean
            (move,float)
            return the max move with its utility value
        """ 
        # monitor time left       
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
            
        # update serach depth
        current_depth=parent_depth+1

        # check if node is a terminal node of the search tree
        if self.terminal_test(game,current_depth,max_search_depth):
            # if this is a terminal node then we evaluate the board
            # WARNING here the active player is the oponent of MyPLayer
            # if we want to evaluate game from MyPlayer point of view then we need to pass the opponent of the opponent 
            res = self.score(game,game.get_opponent(game.active_player))
            return (None,res)
        
        # initialise move and utility value before search and recursive call
        (minMove, minUtility) = (None,float("inf"))
        
        # if not a terminal node then we will test all possible children note
        # children node are here given by all possible legal moves for the active player
        for move in game.get_legal_moves():
            child=game.forecast_move(move)
            # create the children node associated to a move
            # WARNING : forecast return a new board where the active player is changed
            (_,utility) = self.maximise(child,max_search_depth,current_depth)
            
            if utility < minUtility:
                (minMove, minUtility) = (move,utility)
        
        return (minMove, minUtility)



class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        iterative deepening search instead of fixed-depth search.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left
        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        possible_init_moves = game.get_legal_moves(self)
        if len(possible_init_moves) !=0:
            best_move = possible_init_moves[randint(0, len(possible_init_moves) - 1)]
        else:
            best_move = (-1, -1)

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            
            # use iterative deepening starting at depth 1
            # call to alphabeta are repeated with an increased depth while there is some time left
            current_max_depth = 1
            while (self.time_left() - self.TIMER_THRESHOLD > 0) :
                move = self.alphabeta(game, current_max_depth)
                #if search return an invalid move keep previous best move
                if(move != (-1, -1))and(move!=None):
                    best_move=move
                current_max_depth += 1
        
        except SearchTimeout :
            # return best computed move within allowed time
            return best_move

        # Return the best move from the last completed search iteration
        return best_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        This should be a modified version of ALPHA-BETA-SEARCH in the AIMA text
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        # first call is MyPlayer turn, hence shall maximise the value 
        (move,utility) = self.maximise(game,depth,0,alpha,beta)
        return move
                        
    def terminal_test(self, game, current_depth, max_search_depth):
        """Test if the board is a terminal node or if it can be extended

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        current_depth : int
            current depth of the extended tree
            
        max_search_depth : int
            limit of the depth of the search tree
            
        Returns
        -------
        Boolean
            True if it is a terminal node
            False in other cases
        """        
        # can be a terminal node if
        # - reached the maximum depth of search
        # - no more legal moves
        # - or one player loses or win
        if len(game.get_legal_moves()) == 0 or game.utility(game.active_player) !=0 or current_depth>max_search_depth:
            return True
        else:
            False
    
    def maximise(self, game, max_search_depth,parent_depth,alpha,beta):
        """maximise function on minimax algorithm

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        parent_depth : int
            depth of the node from where the function is called
            
        max_search_depth : int
            limit of the depth of the search tree
            
        Returns
        -------
        Boolean
            (move,float)
            return the max move with its utility value
        """ 
        # monitor time left
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        
        # update serach depth
        current_depth=parent_depth+1      
        
        # check if node is a terminal node of the search tree
        if self.terminal_test(game,current_depth,max_search_depth):
            # if this is a terminal node then we evaluate the board
            res = self.score(game,game.active_player)
            return (None,res)
        
        # initialise move and utility value before search and recursive call
        (maxMove, maxUtility) = (None,-float("inf"))
    
        # if not a terminal node then we will test all possible children note
        # children node are here given by all possible legal moves for the active player
        for move in game.get_legal_moves():
            child=game.forecast_move(move)
            # create the children node associated to a move
            # WARNING : forecast return a new board where the active player is changed
            # the children node active player is the opponent
            (_,utility) = self.minimise(child,max_search_depth,current_depth,alpha,beta)
            
            if utility > maxUtility:
                (maxMove, maxUtility) = (move,utility)

            # beta prunning stops the for no need to analyse more
            if maxUtility>= beta:
                break

            # alpha update value
            if maxUtility > alpha:
                alpha = maxUtility
       
        return (maxMove, maxUtility)

    def minimise(self, game, max_search_depth,parent_depth,alpha,beta):
        """minimise function on minimax algorithm

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        parent_depth : int
            depth of the node from where the function is called
            
        max_search_depth : int
            limit of the depth of the search tree
            
        Returns
        -------
        Boolean
            (move,float)
            return the max move with its utility value
        """ 
        # monitor time left       
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
            
        # update serach depth
        current_depth=parent_depth+1

        # check if node is a terminal node of the search tree
        if self.terminal_test(game,current_depth,max_search_depth):
            # if this is a terminal node then we evaluate the board
            # WARNING here the active player is the oponent of MyPLayer
            # if we want to evaluate game from MyPlayer point of view then we need to pass the opponent of the opponent 
            res = self.score(game,game.get_opponent(game.active_player))
            return (None,res)
        
        # initialise move and utility value before search and recursive call
        (minMove, minUtility) = (None,float("inf"))
        
        # if not a terminal node then we will test all possible children note
        # children node are here given by all possible legal moves for the active player
        for move in game.get_legal_moves():
            child=game.forecast_move(move)
            # create the children node associated to a move
            # WARNING : forecast return a new board where the active player is changed
            (_,utility) = self.maximise(child,max_search_depth,current_depth,alpha,beta)

            if utility < minUtility:
                (minMove, minUtility) = (move,utility)
 
            if minUtility<= alpha:
                break

            if minUtility < beta:
                beta = minUtility
       
        return (minMove, minUtility)
