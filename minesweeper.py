
""" 
Objective: to build AI knowledge-base agent capable of playing Minesweeper game. 
This project focuses on Knowledge Engineering, which involves capturing, representing, and organizing knowledge 
in a way that can be effectively utilized by AI models. 
The goal of the knowledge engineering is to make explicit the knowledge that humans possess 
in a particular domain and enable AI systems to reason, learn, and make decisions based on the knowledge.
 """

import itertools
import random
import cProfile


class Minesweeper():
    """
    Represents the MineSweeper game board and provides functionalities related to the game board
    Initialize the game board with height, width and # of mines
    Randomly adds mines to the board
    Provides methods to print the board
    Check if a cell is a mine, and count the num of nearby mines
    Tracks the set of found mines and provides a method to check if all mines are flagged
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i,j))
                self.board[i][j] = True # has mine in that particular cell

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        
        # Prints a text-based representation
        # of where mines are located.
       
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("|", end="")
            print("|")
        print("--" * self.width + "-")


    def __str__(self):
        s = ""
        for i in range(self.height):
            s += "--" * self.width + "-" + "\n"
            for j in range(self.width):
                if self.board[i][j]:
                    s += "|X"
                else:
                    s += "| "
            s += "|" + "\n"
        s += "--" * self.width + "-"
        return s


    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]


    def nearby_mines(self, cell) -> int:
        count = 0
        # Loop over all cells within one row and column
        # search row (first element of cell) from row - 1 to row + 1
        for i in range(cell[0] - 1, cell[0] + 2): # horizontal check
            for j in range(cell[1] - 1, cell[1] + 2): # vertical check

                # Ignore the cell itself
                if (i,j) == cell:
                    continue
                
                # Update count
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1
        return count


    def won(self) -> bool:
        return self.mines_found == self.mines


class Sentence():
    """
    represent a logical statement (knowledge) about the Minesweeper game,
    which consists of a set of cells and a count of # of mines among the cells
    Stores the set of cells and the count
    Provides methods to identify known mines and known safe cells within the set
    Allows marking a cell as a mine or safe, updating the internal knowledge representation
    """

    def __init__(self, cells, count):
        self.cells = set(cells) # board of cells
        self.count = count #  count mine cell
        self.safes = set()
        self.mines = set()

    def __eq__(self, other) -> bool:
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
         return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.cells if len(self.cells) == self.count else set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.cells if self.count == 0 else set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        if cell is in the sentence, the function should update the sentence 
        so that cell is no longer in the sentence
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1 # Update mine count
            self.mines.add(cell) # Update mines

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        if cell is in the sentence, the function should update the sentence 
        so that cell is no longer in the sentence
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.safes.add(cell) # Update safes


class MinesweeperAI():
    """
    Represents the Minesweeper game player (AI) and provides strategies for playing the game
    Initialize the AI with the game board's height and width
    Tracks the moves made, known mines, known safes and a list of logical sentences (Knowledge)
    Provides methods to mark a cell as a mine or safe, and update the knowledge based on the marked cells
    Makes safe moves by choosing a cell that is known to be safe and not already chosen
    Makes random moves by choosing a cell randomly among the remaining unchosen cells
    The AI uses the knowledge base to make informed moves and infer new information
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []


    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)
        
        #print("Knowledge Base after marking mine:", self.knowledge)
        #print("Mines:", self.mines)
        #print("Safes:", self.safes)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
        
        #print("Knowledge Base after marking safe:", self.knowledge)
        #print("Mines:", self.mines)
        #print("Safes:", self.safes)

    def add_knowledge(self, cell, count):
        # 1
        self.moves_made.add(cell)
        # 2
        self.mark_safe(cell)
        # 3
        surrounding_cells = set()

        if count == 0:
            for surrounding_cell in surrounding_cells:
                self.mark_safe(surrounding_cell)
        elif count == len(surrounding_cells):
            for surrounding_cell in surrounding_cells:
                self.mark_mine(surrounding_cell)

        i,j = cell
        for x in range(i-1, i+2):
            for y in range(j-1, j+2):
                # ensure not to include the current cell and stay within the range of the game board
                if (x, y) != cell and 0 <= x < self.height and 0 <= y < self.width:
                    # add cells to neighboring cell set
                    surrounding_cells.add((x,y))
        # Create a new Sentence object which represents the updated knowledge
        # with current 'cell' has 'count' mines in neighboring cells
        # Add this new Sentence object to the knowledge list
        self.knowledge.append(Sentence(surrounding_cells, count))
        #4
        new_safe_cells = set()
        new_mine_cells = set()
        for sentence in self.knowledge:
            known_safes = sentence.known_safes()
            known_mines = sentence.known_mines()
            if known_safes:
                new_safe_cells.update(known_safes)
            if known_mines:
                new_mine_cells.update(known_mines)
        
        for cell in new_safe_cells:
            self.mark_safe(cell)
        for cell in new_mine_cells:
            self.mark_mine(cell)

        #5
        new_sentences = [] # Set doesn't work because it's not hashable
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 == sentence2:
                    continue
                # check if sentence1.cells is a subset of sentence2.cells
                if sentence1.cells.issubset(sentence2.cells): #bool
                    # if true, then the difference can be inferred as new knwoledge
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count
                    # creat a new Sentence object with updated cells and count
                    # and append it to the new_sentence list
                    new_sentence = Sentence(new_cells, new_count)
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)
                elif sentence2.cells.issubset(sentence1.cells):
                    new_cells = sentence1.cells - sentence2.cells
                    new_count = sentence1.count - sentence2.count
                    new_sentence = Sentence(new_cells, new_count)
                    if new_sentence not in self.knowledge:
                        print("New inferred knowledge:", new_sentence)
                        self.knowledge.append(new_sentence)
        # add the new sentences to the knowledge base
        #self.knowledge.extend(new_sentences)

        # print("Knowledge Base after adding new sentence:", self.knowledge)
        print("Mines:", self.mines)
        print("Safes:", self.safes)
        #print("Knowledge", self.knowledge)
        print("Current AI Knowldge Base length:", len(self.knowledge))

    def make_safe_move(self):
        for cell in self.safes:
            if cell not in self.moves_made:
                print("Make Safe Move:", cell)
                return cell
        return None


    def make_random_move(self):
        moves_left = []
        for i in range(self.height):
            for j in range(self.width):
                cell = (i,j)
                if cell not in self.moves_made and cell not in self.mines:
                    moves_left.append(cell)
        if moves_left:
            # print("Available moves:", moves_left)
            random_move = random.choice(moves_left)
            print("Random move selected:", random_move)
            return random_move
        
        print("No available moves.")
        return None


""" 
minesweeper_ai = MinesweeperAI()
cProfile.run('minesweeper_ai.add_knowledge((1,2),5)')
 """