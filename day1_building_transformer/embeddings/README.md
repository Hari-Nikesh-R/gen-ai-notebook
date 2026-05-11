# Embedding

An embedding is a vector representation of a token.

Instead of:
```python
"ai" → 4
```

we convert it into:
```python
"ai" → [0.2, -0.8, 1.5, 0.7]
```
Now AI can do:

1. Mathematics
2. Similarity comparison
3. Learning
4. Attention computation

## Why Vectors?

Because neural networks work with:

- numbers
- tensors
- matrices

NOT words.

## Embedding Table

Transformers use embedding matrices

Think of it like:

| Token  | Vector            |
|--------|-------------------|
| ai     | [0.2, 0.8, -0.1]  |
| love   | [1.2, -0.5, 0.7]  |
| python | [0.9, 0.1, -0.4]  |

This table is learned during training.

Previously we are looking into the tokenization part.
Now with the tokenizer we can encode the text into token IDs.
Now with the token IDs we need to convert them into embeddings.
So we will create an embedding matrix for the vocabulary.
This embedding matrix will be learned during training.

### Step 1
#### Creating Vocabulary
```python
vocab = {
    "<PAD>": 0,
    "i": 1,
    "love": 2,
    "ai": 3
}
```

### Step 2
#### Choose the embedding dimension
Suppose:
```
embedding_dim = 4
```
Meaning each token gets:
```
"ai" → [0.1, 0.7, -0.2, 1.5]
```

### Step 3
#### Create Random Embeddings
```python
import numpy as np

vocab = {
    "<PAD>": 0,
    "i": 1,
    "love": 2,
    "ai": 3
}

embedding_dim = 4

embedding_matrix = np.random.rand(len(vocab), embedding_dim)

print(embedding_matrix)
```
What Happened?

Suppose output: 
```
[
 [0.11, 0.45, 0.23, 0.91],   # <PAD>
 [0.77, 0.12, 0.56, 0.34],   # i
 [0.66, 0.88, 0.25, 0.44],   # love
 [0.91, 0.33, 0.72, 0.15]    # ai
]
```
Each row =
embedding vector for one token.
