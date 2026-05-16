# What We Are Building

We will train:
**Sentiment Analysis Model**

**Input:**
> "I love this movie"

**Output:**
> Positive

This teaches:
* datasets
* tokenization
* transformers
* training
* evaluation
* inference
* saving models

This is the foundation of almost ALL NLP systems.

## PART 2 — Open Google Colab

Open:
[Google Colab](#)

## PART 3 — Create New Notebook

Click:
`File` → `New Notebook`

Rename notebook:
`hf_training_beginner.ipynb`

## PART 4 — Enable GPU (VERY IMPORTANT)

Without GPU training becomes slow.

Go to:
`Runtime` → `Change runtime type`

Select:
`T4 GPU`

Click **Save**.

## PART 5 — Verify GPU

In first cell paste:
```python
import torch

print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

Expected:
```
True
Tesla T4
```

### WHY GPU?

Training means:
* millions/billions of matrix calculations
* CPUs are slow
* GPUs do parallel math operations

AI training = mostly matrix multiplication.

## PART 6 — Install Hugging Face Libraries

New cell:
```bash
!pip install transformers datasets accelerate evaluate -q
```

### WHAT ARE THESE?

| Library | Purpose |
| --- | --- |
| transformers | Models like BERT |
| datasets | Download datasets |
| accelerate | Faster GPU training |
| evaluate | Accuracy metrics |

## PART 7 — Import Libraries

```python
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

import evaluate
import numpy as np
```

### WHY THESE IMPORTS?

#### AutoTokenizer
Converts text → numbers.

**Example:**
"I love AI"

Becomes:
`[101, 1045, 2293, 9932, 102]`

Computers only understand numbers.

#### AutoModelForSequenceClassification
Loads pretrained BERT.

BERT already knows:
* grammar
* sentence structure
* language patterns

We only “fine-tune” it.

#### Trainer
Industry training helper.

Instead of manually writing:
* training loop
* optimizer
* gradient handling

Trainer automates it.

## PART 8 — Load Dataset

```python
dataset = load_dataset("imdb")
```

### WHAT IS HAPPENING HERE?
Hugging Face downloads IMDB movie reviews dataset.

**Example:**

| Review | Label |
| --- | --- |
| Amazing movie | Positive |
| Waste of time | Negative |

### Explore Dataset
```python
print(dataset)
```

Expected:
```python
DatasetDict({
    train: Dataset(...)
    test: Dataset(...)
})
```

### See One Example
```python
print(dataset["train"][0])
```

## PART 9 — Load Tokenizer

```python
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
```

### WHY TOKENIZER IS NEEDED?
Transformers cannot read raw text.

They need:
`Text` → `Tokens` → `Token IDs` → `Embeddings`

**Pipeline:**
Sentence
↓
Tokenizer
↓
Token IDs
↓
Embeddings
↓
Transformer

## PART 10 — Tokenization

```python
def tokenize_function(example):
    return tokenizer(
        example["text"],
        padding="max_length",
        truncation=True
    )
```

### WHAT IS PADDING?
Different sentences have different lengths.

**Example:**
"I love AI"
*vs*
"I absolutely love studying artificial intelligence"

Neural networks need SAME SIZE input.
So shorter sentences get padded.

### WHAT IS TRUNCATION?
Long sentences get cut.
Because models have max token limits.

## PART 11 — Apply Tokenization

```python
tokenized_datasets = dataset.map(
    tokenize_function,
    batched=True
)
```

### Inspect Tokenized Data
```python
print(tokenized_datasets["train"][0])
```

You’ll now see:
* `input_ids`
* `attention_mask`
* `label`

### WHAT IS ATTENTION MASK?
Example:
* Real token = 1
* Padding token = 0

This tells transformer:
*"Ignore padding"*

## PART 12 — Use Small Dataset First

IMPORTANT INDUSTRY PRACTICE.
Never start training huge datasets first.

```python
small_train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(1000))
small_test_dataset = tokenized_datasets["test"].shuffle(seed=42).select(range(200))
```

### WHY?
Benefits:
* faster debugging
* cheaper
* easier experimentation
* quicker iteration

Industry teams ALWAYS test on small subsets first.

## PART 13 — Load Pretrained Model

```python
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=2
)
```

### WHAT IS HAPPENING HERE?
We download pretrained BERT.
Then modify last layer:
* Positive
* Negative

This is called:
**Fine-Tuning**

We reuse existing intelligence.

## PART 14 — Define Accuracy Metric

```python
metric = evaluate.load("accuracy")
```

## PART 15 — Compute Accuracy Function

```python
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    
    predictions = np.argmax(logits, axis=-1)
    
    return metric.compute(
        predictions=predictions,
        references=labels
    )
```

### WHAT ARE LOGITS?
Raw prediction scores.

**Example:**
`[2.1, -1.4]`

Means:
*Positive probability higher*

### WHY ARGMAX?
Find highest probability class.

**Example:**
`[0.2, 0.8]`

Prediction:
*Class 1*

## PART 16 — Training Configuration

```python
training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=1,
    weight_decay=0.01
)
```

### IMPORTANT PARAMETERS

#### learning_rate
Controls: How fast model learns
* Too high: ❌ unstable
* Too low: ❌ slow learning

#### batch_size
How many samples at once.
Example: *8 reviews per step*

#### epochs
How many full passes through dataset.

## PART 17 — Create Trainer

```python
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=small_train_dataset,
    eval_dataset=small_test_dataset,
    compute_metrics=compute_metrics
)
```

## PART 18 — START TRAINING

```python
trainer.train()
```

NOW:
* forward propagation
* loss calculation
* backpropagation
* weight updates

are happening internally.

### WHAT IS BACKPROPAGATION?
Core of deep learning.

Process:
Prediction
↓
Error
↓
Adjust weights
↓
Better prediction

This repeats thousands of times.

## PART 19 — Evaluate Model

```python
trainer.evaluate()
```

Expected:
`accuracy: 0.85+`

## PART 20 — Save Model

```python
trainer.save_model("./my_model")
tokenizer.save_pretrained("./my_model")
```

### WHY SAVE?
Otherwise training is lost.

Saved model can later:
* deploy
* share
* upload
* reuse

## PART 21 — Test Model

```python
from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model="./my_model"
)
```

### Run Prediction

```python
result = classifier(
    "This movie was fantastic!"
)

print(result)
```

Expected:
`POSITIVE`

## PART 22 — Real Understanding

You just built:

Raw Text
↓
Tokenization
↓
Token IDs
↓
Embeddings
↓
Transformer Layers
↓
Classification Head
↓
Prediction

THIS is real NLP engineering.

## PART 23 — Industry Workflow

Real companies do:

Collect data
↓
Clean data
↓
Tokenize
↓
Fine-tune
↓
Evaluate
↓
Deploy
↓
Monitor

You already completed most of it.

## PART 24 — COMMON BEGINNER ERRORS

### Error 1
CUDA out of memory

Fix:
`batch_size = 4`

### Error 2
Tokenizer mismatch

Always use:
`same tokenizer + same model`

### Error 3
Training too slow.

Fix:
* enable GPU
* use smaller dataset

## PART 25 — YOUR PRACTICAL TASK

Now YOU modify code.

### TASK 1
Train on:
`2000 samples`

### TASK 2
Increase:
`epochs = 3`

Observe:
* accuracy changes
* training time changes

### TASK 3
Test custom sentences:
* "I hated this movie"
* "This film was mind blowing"