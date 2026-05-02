"""Tests for rag-loader text chunker."""

import pytest

from rag_loader.chunker import chunk_text


def test_empty_string() -> None:
    """Test that empty input returns an empty list."""
    assert chunk_text("") == []


def test_whitespace_only() -> None:
    """Test that whitespace-only input returns an empty list."""
    assert chunk_text("   \n\n  ") == []


def test_short_text_single_chunk() -> None:
    """Test that text shorter than chunk_size returns one chunk."""
    result = chunk_text("Hello world", chunk_size=100)
    assert len(result) == 1
    assert result[0] == "Hello world"


def test_two_paragraphs_split_on_double_newline() -> None:
    """Test that two short paragraphs split on paragraph boundary."""
    text = "First paragraph.\n\nSecond paragraph."
    result = chunk_text(text, chunk_size=20, chunk_overlap=0)
    assert len(result) == 2
    assert "First paragraph." in result[0]
    assert "Second paragraph." in result[1]


def test_long_paragraph_splits_on_sentence() -> None:
    """Test that a long paragraph without newlines splits on sentences."""
    text = "Sentence one is here. Sentence two is here. Sentence three is here."
    result = chunk_text(text, chunk_size=45, chunk_overlap=0)
    assert len(result) >= 2
    for chunk in result:
        assert len(chunk) <= 45


def test_splits_on_words_when_no_sentences() -> None:
    """Test fallback to word splitting when no sentence boundaries exist."""
    text = "alpha bravo charlie delta echo foxtrot golf hotel"
    result = chunk_text(text, chunk_size=20, chunk_overlap=0)
    assert len(result) >= 2
    for chunk in result:
        assert len(chunk) <= 20


def test_no_chunk_exceeds_size() -> None:
    """Test that no chunk exceeds chunk_size for various inputs."""
    text = (
        "Fluffy Cake is a SaaS platform. "
        "It helps teams build ML platforms. "
        "Users define pipelines as code. "
        "The engine handles scaling. "
        "Models are served via KServe."
    )
    result = chunk_text(text, chunk_size=60, chunk_overlap=10)
    for chunk in result:
        assert len(chunk) <= 60, f"Chunk too long ({len(chunk)}): {chunk!r}"


def test_overlap_between_chunks() -> None:
    """Test that consecutive chunks share overlapping text."""
    text = "aa bb cc dd ee ff gg hh ii jj"
    result = chunk_text(text, chunk_size=15, chunk_overlap=5)
    assert len(result) >= 2
    # Check that some tail of chunk[i] appears in chunk[i+1]
    for i in range(len(result) - 1):
        tail = result[i][-5:]
        assert tail in result[i + 1] or result[i + 1].startswith(tail.lstrip()), (
            f"No overlap between chunk {i} and {i + 1}: {result[i]!r} -> {result[i + 1]!r}"
        )


def test_overlap_small_example() -> None:
    """Test overlap with chunk_size=10 and chunk_overlap=3."""
    text = "aa bb cc dd ee ff"
    result = chunk_text(text, chunk_size=10, chunk_overlap=3)
    assert len(result) >= 2
    for chunk in result:
        assert len(chunk) <= 10


def test_single_long_word_returned_as_is() -> None:
    """Test that a single word exceeding chunk_size is not dropped."""
    long_word = "a" * 100
    result = chunk_text(long_word, chunk_size=10, chunk_overlap=3)
    assert len(result) >= 1
    joined = "".join(result)
    assert len(joined) >= 100


def test_overlap_ge_chunk_size_raises() -> None:
    """Test that chunk_overlap >= chunk_size raises ValueError."""
    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_text("hello", chunk_size=10, chunk_overlap=10)


def test_overlap_greater_than_chunk_size_raises() -> None:
    """Test that chunk_overlap > chunk_size raises ValueError."""
    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_text("hello", chunk_size=10, chunk_overlap=15)


def test_real_document_chunking() -> None:
    """Test chunking on a realistic multi-paragraph document."""
    text = (
        "# Fluffy Cake Overview\n\n"
        "Fluffy Cake is a SaaS platform that lets teams build ML platforms.\n\n"
        "With Fluffy Cake, data engineers define their ML platform as code. "
        "The platform provisions compute, storage, and model registries automatically. "
        "Teams go from raw data to production models in hours."
    )
    result = chunk_text(text, chunk_size=120, chunk_overlap=20)
    assert len(result) >= 2
    for chunk in result:
        assert len(chunk) <= 120
    # All original content should be represented
    joined = " ".join(result)
    assert "Fluffy Cake" in joined
    assert "production models" in joined
