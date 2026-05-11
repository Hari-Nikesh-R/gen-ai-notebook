raw_text = "I love AI, and AI loves me"

class SimpleTokenizer:
    def __init__(self, text):
        self.text = text
        self.tokens = self._simple_tokenizer(text)

    def _simple_tokenizer(self, text):
        text = text.lower()
        tokens = text.split()
        return tokens
    
    def _vocubulary_mapping(self):
        vocab = {}
        for index, token in enumerate(self.tokens):
            if (token not in vocab):
                # As a best practice we need not to overight the words which is actually in there.
                vocab[token] = index + 1
        return vocab

    def _vocubulary_demapping(self):
        reverse_vocab = {}  
        vocab = self._vocubulary_mapping()
        for word, index in vocab.items():
            reverse_vocab[index] = word
        return reverse_vocab
    
    def encoding(self):
        vocab = self._vocubulary_mapping()
        encoded_text = [vocab[token] for token in self.tokens]
        return encoded_text
  

    def decoding(self):
        vocab = self._vocubulary_demapping()
        decoded_text = [vocab[token] for token in vocab]
        return decoded_text

t = SimpleTokenizer(raw_text)
print(t.encoding())
print(t.decoding())

