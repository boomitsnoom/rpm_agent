# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
from PIL import Image , ImageChops, ImageOps, ImageMath, ImageFilter, ImageStat
import numpy as np

class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):

        # Heuristic Functions
        self.heuristic_functions = {"FH" : final_heuristic}

        # Voting Trios
        self.horizontal_voting_trio = [("A","B","C"),("D","E","F")]
        self.vertical_voting_trio = [("A","D","G"),("B","E","H")]
        self.voting_trios_dict = {"horizontal" : self.horizontal_voting_trio, "vertical": self.vertical_voting_trio}
        self.query_image_trio_dict = {"horizontal" : ("G","H"), "vertical" : ("C","F")}
        
    def establish_voting_pairs(self,problem):
        if problem.problemType == "3x3":
            self.horizontal_voting_pairs = [("A","B"),("B","C"),("D","E"),("E","F"),("G","H")]
            self.vertical_voting_pairs   = [("A","D"),("D","G"),("B","E"),("E","H"),("C","F")]
            self.diagonal_voting_pairs   = [("A","E")]
            self.voting_pairs_dict = {"horizontal" : self.horizontal_voting_pairs, "vertical": self.vertical_voting_pairs, "diagonal" : self.diagonal_voting_pairs}
            self.query_image_dict = {"horizontal" : "H", "vertical" : "F", "diagonal" : "E"}
        elif problem.problemType == "2x2":
            self.horizontal_voting_pairs = [("A","B")]
            self.vertical_voting_pairs   = [("A","C")]
            self.voting_pairs_dict = {"horizontal" : self.horizontal_voting_pairs, "vertical": self.vertical_voting_pairs}
            self.query_image_dict = {"horizontal" : "C", "vertical" : "B"}
    
    def cast_vote_pair(self,orientation,heuristic,problem_name):
        # Establish the voting pair and specified heuristic
        voting_pairs = self.voting_pairs_dict[orientation]
        visual_heuristic = self.heuristic_functions[heuristic]
        query_image = self.given_images_dict[self.query_image_dict[orientation]]
        for p0,p1 in voting_pairs:
            dtype = [('answer_number', int),('dpr', float), ('ipr', float)]
            answers_list = []
            target_tuple = visual_heuristic(self.given_images_dict[p0],self.given_images_dict[p1])

            for index, answer_choice in enumerate(self.candidate_images_dict):
                answer_tuple =  visual_heuristic(query_image,self.candidate_images_dict[answer_choice])
                closeness = (int(answer_choice),abs(target_tuple[0]-answer_tuple[0]),abs(target_tuple[1]-answer_tuple[1]))
                answers_list.append(closeness)

            # Sort by DPR, if there are ties, check by IPR
            np_answers_list = np.array(answers_list, dtype=dtype)
            sorted_np_answers_list = np.sort(np_answers_list, order=['dpr', 'ipr']) 
            closest = sorted_np_answers_list[0][0]
            self.votes[str(closest)] += 1
        
    def cast_vote_trio(self,orientation,heuristic,problem_name):
        # Establish the voting pair and specified heuristic
        voting_trio = self.voting_trios_dict[orientation]
        visual_heuristic = self.heuristic_functions[heuristic]
        query_pair = list(self.query_image_trio_dict[orientation])

        target_images = []
        for p0,p1,p2 in voting_trio:
            target_image = row_xor(self.given_images_dict[p0], self.given_images_dict[p1], self.given_images_dict[p2])
            target_images.append(target_image)

        target_tuple = visual_heuristic(target_images[0],target_images[1])

        for target_image in target_images:
            dtype = [('answer_number', int),('dpr', float), ('ipr', float)]
            answers_list = np.zeros((len(self.candidate_images_dict)))

            for index,answer_choice in enumerate(self.candidate_images_dict):
                #print(answer_choice)
                answer_xor_image = row_xor(self.given_images_dict[query_pair[0]], self.given_images_dict[query_pair[1]], self.candidate_images_dict[answer_choice])

                # Converty to numpy arrays
                target_pixels = np.array(target_image)
                target_pixels = target_pixels.astype(int)
                target_pixels = target_pixels.flatten()

                answer_pixels = np.array(answer_xor_image)
                answer_pixels = answer_pixels.astype(int)
                answer_pixels = answer_pixels.flatten()

                dist = np.linalg.norm(target_pixels - answer_pixels)
                answers_list[index] = dist

            closest = np.argmin(answers_list)
            closest_val = np.min(answers_list)
            std = np.std(answers_list)
            mean = np.mean(answers_list)

            closest += 1 

            self.votes[str(closest)] += 1


    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an int representing its
    # answer to the question: 1, 2, 3, 4, 5, or 6. Strings of these ints 
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName(). Return a negative number to skip a problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self,problem):
        # Step 0: Establish the voting pairs and potential votes on the ballot
        # Step 1: Prepare the voting pairs
        self.establish_voting_pairs(problem)
        # Step 2: Prepare the Images
        self.given_images_dict, self.candidate_images_dict = prepare_images(problem)
        
        
        self.votes = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0}
    
        # Step 3: Vote!
        for orientation in self.voting_pairs_dict:
            for heuristic in self.heuristic_functions:
                self.cast_vote_pair(orientation,heuristic,problem.name)

        if problem.problemType == "3x3":
            # Step 4: Voting using trios
            for orientation in self.voting_trios_dict:
                for heuristic in self.heuristic_functions:
                    self.cast_vote_trio(orientation,heuristic,problem.name)

        #print(self.votes)
        winner = max(self.votes, key=self.votes.get)
        #print(self.votes)
        #print(int(winner))
        return int(winner)

def prepare_images(problem):
    given_images_dict = {}
    candidate_images_dict = {}
    for figure in problem.figures:
        image = Image.open(problem.figures[figure].visualFilename)
        image = ImageOps.grayscale(image)
        image = image.point(lambda x: 0 if x<128 else 255, '1')
        if figure == "A" or figure == "B" or figure == "C" or figure == "D" or figure == "E" or figure == "F" or figure == "G" or figure == "H":
            given_images_dict[figure] = image
        else:
            candidate_images_dict[figure] = image
    return given_images_dict,candidate_images_dict

def check_dpr(image1,image2):   # Dark Pixel Ratio
    num_black_pixels_1 =  image1.histogram()[0]
    num_white_pixels_1 =  image1.histogram()[255]
    num_black_pixels_2 =  image2.histogram()[0]
    num_white_pixels_2 =  image2.histogram()[255]
    ratio1 = num_black_pixels_1 / (num_black_pixels_1 + num_white_pixels_1)
    ratio2 = num_black_pixels_2 / (num_black_pixels_2 + num_white_pixels_2)
    return abs(ratio1 - ratio2)

def check_ipr(image1,image2):   # (Dark) Intersection Pixel Ratio
    or_image = ImageChops.logical_or(image1,image2)
    total_num_black_pixels =  or_image.histogram()[0]
    num_black_pixels_1 =  image1.histogram()[0]
    num_black_pixels_2 =  image2.histogram()[0]
    return total_num_black_pixels / (num_black_pixels_1 + num_black_pixels_2)

def final_heuristic(image1,image2):
    dpr = check_dpr(image1,image2)
    ipr = check_ipr(image1,image2)
    return (dpr, 1 - ipr)

def row_xor(image1,image2,image3):
    pair_xor = ImageChops.logical_xor(image1,image2)
    trio_xor = ImageChops.logical_xor(pair_xor,image3)
    return trio_xor