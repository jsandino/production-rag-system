from app.core.chunker import Chunker


class FakeTokenizer:
    """Tokenizer fake that treats each character as one token."""

    def encode(self, text: str) -> list[int]:
        return [ord(c) for c in text]

    def decode(self, tokens: list[int]) -> str:
        return "".join(chr(t) for t in tokens)


def make_chunker(max_tokens: int, overlap: int = 0) -> Chunker:
    return Chunker(tokenizer=FakeTokenizer(), max_tokens=max_tokens, overlap=overlap)


def test_empty_text_returns_empty_list():
    chunker = make_chunker(max_tokens=10)
    assert chunker.split("") == []


def test_short_text_returns_single_chunk():
    chunker = make_chunker(max_tokens=10)
    assert chunker.split("hello") == ["hello"]


def test_long_text_is_split_into_multiple_chunks():
    chunker = make_chunker(max_tokens=3, overlap=0)
    chunks = chunker.split("abcdef")
    assert chunks == ["abc", "def"]


def test_overlap_repeats_tokens_across_chunks():
    chunker = make_chunker(max_tokens=4, overlap=2)
    # step = max_tokens - overlap = 2, so chunks start at 0, 2, 4
    chunks = chunker.split("abcdef")
    assert chunks == ["abcd", "cdef", "ef"]


def test_text_not_divisible_by_chunk_size():
    chunker = make_chunker(max_tokens=4, overlap=0)
    chunks = chunker.split("abcde")
    assert chunks == ["abcd", "e"]
