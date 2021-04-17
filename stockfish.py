#https://pypi.org/project/stockfish/
#https://stockfishchess.org/download/
#I used Linux 64-bit but the compiled versions should work fine
#Michael's Location: "/mnt/c/Users/micha/Desktop/3D Stuff/light-blue/stockfish_20090216_x64"
#Michael's laptop location (blade and thinkpad): "/home/michael/Desktop/light-blue/stockfish_20090216_x64"
#Change the location below to yours (or add to path)
from stockfish import Stockfish
stockfish = Stockfish("/home/michael/Desktop/light-blue/stockfish_20090216_x64",parameters={"Threads": 2})

print(stockfish.get_best_move())
stockfish.set_position(['d2d4', 'e7e6'])        #Position as a list of all moves made in order
print(stockfish.get_best_move())

stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")  #Starting position in FEN notation 
print(stockfish.get_best_move())
stockfish.set_fen_position("rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2")  #After 2 moves

move = stockfish.get_best_move()
print(move)

print(stockfish.get_fen_position())

print(stockfish.get_board_visual())
