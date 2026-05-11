import re

class Tokenizer:
    def __init__(self, sentences: list[str]):
        """
        Args:
            sentences: A list of raw text strings to tokenize.
        """
        self.sentences = sentences
        self.special_tokens = {"<PAD>": 0, "<UNK>": 1}
        self.tokenized_sentences = self._tokenize_all(sentences)
        self.vocab = self._build_vocabulary(self.tokenized_sentences)
        self.reverse_vocab = {idx: word for word, idx in self.vocab.items()}

    def _tokenize_sentence(self, text: str) -> list[str]:
        """Lowercase and split a single string into tokens."""
        text = text.lower()
        tokens = re.findall(r'\w+|[^\w\s]', text)
        return tokens

    def _tokenize_all(self, sentences: list[str]) -> list[list[str]]:
        """Tokenize every sentence in the list."""
        return [self._tokenize_sentence(s) for s in sentences]

    def _build_vocabulary(self, tokenized_sentences: list[list[str]]) -> dict[str, int]:
        """
        Build a shared vocabulary across all sentences.
        Index 0 → <PAD>, Index 1 → <UNK>, then unique words in order.
        """
        vocab = dict(self.special_tokens)          # start with special tokens
        for tokens in tokenized_sentences:
            for token in tokens:
                if token not in vocab:
                    vocab[token] = len(vocab)
        return vocab

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def encoding(self) -> list[list[int]]:
        """
        Encode each sentence into a list of token IDs.

        Returns:
            A list of lists, where each inner list contains the token IDs
            for the corresponding sentence.
        """
        encoded = []
        for tokens in self.tokenized_sentences:
            ids = [self.vocab.get(token, self.vocab["<UNK>"]) for token in tokens]
            encoded.append(ids)
        print("\nENCODED SENTENCES:")
        for i, enc in enumerate(encoded):
            print(f"  Sentence {i+1}: {enc}")
        return encoded

    def decoding(self, encoded_sentences: list[list[int]] = None) -> list[list[str]]:
        """
        Decode a list of token-ID sequences back to word lists.

        Args:
            encoded_sentences: Output of encoding(). If None, encodes
                               self.sentences first.

        Returns:
            A list of lists, where each inner list contains the decoded words.
        """
        if encoded_sentences is None:
            encoded_sentences = self.encoding()

        decoded = []
        for ids in encoded_sentences:
            words = [self.reverse_vocab.get(i, "<UNK>") for i in ids]
            decoded.append(words)

        print("\nDECODED SENTENCES:")
        for i, dec in enumerate(decoded):
            print(f"  Sentence {i+1}: {dec}")
        return decoded

    def padding(self, max_length: int = None) -> list[list[int]]:
        """
        Pad (or truncate) encoded sentences so every sequence has the same length.

        Args:
            max_length: Target length. If None, uses the length of the longest
                        encoded sentence.

        Returns:
            A list of padded token-ID sequences.
        """
        encoded_sentences = self.encoding()

        if max_length is None:
            max_length = max(len(s) for s in encoded_sentences)

        print("\nMAX LENGTH:")
        print(max_length)

        pad_id = self.vocab["<PAD>"]
        padded_sentences = []

        for sentence in encoded_sentences:
            padded = sentence[:max_length]                      # truncate if too long
            padded = padded + [pad_id] * (max_length - len(padded))  # pad if too short
            padded_sentences.append(padded)

        print("\nPADDED OUTPUT:")
        for i, padded in enumerate(padded_sentences):
            print(f"  Sentence {i+1}: {padded}")

        return padded_sentences

    def vocabulary(self) -> dict[str, int]:
        """Return the full vocabulary mapping (word → ID)."""
        print("\nVOCABULARY:")
        print(self.vocab)
        return self.vocab


if __name__ == "__main__":
    raw_sentences = [
        "I love AI, and AI loves me",
        "https://example.com",
        "2025",
        "if(x > 5):",
    ]

    t = Tokenizer(raw_sentences)

    print("=" * 50)
    print("TOKENIZED SENTENCES:")
    for i, toks in enumerate(t.tokenized_sentences):
        print(f"  Sentence {i+1}: {toks}")

    print("=" * 50)
    t.vocabulary()

    print("=" * 50)
    encoded = t.encoding()

    print("=" * 50)
    t.decoding(encoded)

    print("=" * 50)
    t.padding()