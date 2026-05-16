from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# -------------------------
# Load Model
# -------------------------

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-2b",
    max_seq_length = 2048,
    dtype = None,
    load_in_4bit = True,
)

# -------------------------
# Add LoRA Adapters
# -------------------------

model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj"
    ],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = True,
)

# -------------------------
# Load Dataset
# -------------------------

dataset = load_dataset(
    "json",
    data_files = "dataset.jsonl",
    split = "train"
)

# -------------------------
# Format Dataset
# -------------------------

def formatting_prompts_func(example):
    text = f"""
### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}
"""
    return { "text": text }

dataset = dataset.map(formatting_prompts_func)

# -------------------------
# Trainer
# -------------------------

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = 2048,

    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60,
        learning_rate = 2e-4,
        logging_steps = 1,
        output_dir = "outputs",
        optim = "adamw_8bit",
        fp16 = True,
    ),
)

# -------------------------
# Train
# -------------------------

trainer.train()

# -------------------------
# Save Model
# -------------------------

model.save_pretrained_merged(
    "question-generator-model",
    tokenizer,
    save_method = "merged_16bit",
)