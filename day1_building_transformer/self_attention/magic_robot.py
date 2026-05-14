import numpy as np

def softmax(x):
    """A magic spell to turn numbers into friendship percentages!"""
    # We subtract the max for stability, but it's the same magic math
    exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)

class MagicRobotAttention:
    """
    This is our Magic Robot (Self-Attention mechanism).
    It helps words figure out which other words are their best friends!
    """
    def __init__(self, block_size):
        # We need 3 magic spells (weight matrices) for Query, Key, and Value
        # We use random numbers to initialize our magic.
        self.Wq = np.random.rand(block_size, block_size)
        self.Wk = np.random.rand(block_size, block_size)
        self.Wv = np.random.rand(block_size, block_size)
        
    def play_matching_game(self, lego_blocks):
        print("--- 🤖 The Magic Robot is starting the Matching Game! ---\n")
        
        # STEP 4: Give the magical cards to the words!
        Q = lego_blocks @ self.Wq  # The 'What I want' cards
        K = lego_blocks @ self.Wk  # The 'What I have' cards
        V = lego_blocks @ self.Wv  # The 'My secret' cards
        
        print("1. 🕵️‍♂️ Here are the Query cards (What I want):")
        print(Q, "\n")
        print("2. 🏷️ Here are the Key cards (What I have):")
        print(K, "\n")
        print("3. 🎁 Here are the Value cards (My secret):")
        print(V, "\n")
        
        # STEP 5: Play the Matching Game! 
        # (Words compare their Query cards with everyone's Key cards)
        scores = Q @ K.T
        print("4. 🎲 Who matches with who? (Attention Scores):")
        print(scores, "\n")
        
        # STEP 6: Calm Down the Magic! 
        # (Scaling down so things don't get too crazy)
        dk = K.shape[1]
        scaled_scores = scores / np.sqrt(dk)
        print("5. 🧘 Calmed down magic (Scaled Scores):")
        print(scaled_scores, "\n")
        
        # STEP 7: Find the Best Friends! 
        # (Turn scores into percentages where 1.0 means 100% best friends)
        attention_weights = softmax(scaled_scores)
        print("6. 🤝 Friendship levels! (Softmax Percentages):")
        print(attention_weights, "\n")
        
        # STEP 8: The Final Magic Trick!
        # (Words share their Value secrets with their best friends)
        output = attention_weights @ V
        print("7. ✨ The final magic output (Shared Secrets):")
        print(output, "\n")
        print("Ta-Da! The robot understands the words perfectly now!")
        
        return output

if __name__ == "__main__":
    # Our words: 'i', 'love', 'ai' turned into numbers (Lego blocks)
    # Since each word has 3 numbers, our block_size is 3.
    embeddings = np.array([
        [1.0, 0.0, 1.0],   # i
        [0.0, 2.0, 0.0],   # love
        [1.0, 1.0, 0.0]    # ai
    ])
    
    print("🧩 Our starting Lego blocks (Words):\n", embeddings, "\n")
    
    # Create the robot
    robot = MagicRobotAttention(block_size=3)
    
    # Play the game!
    final_output = robot.play_matching_game(embeddings)
