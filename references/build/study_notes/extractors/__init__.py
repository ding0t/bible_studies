from study_notes.extractors.numeric_id import NumericIdExtractor
from study_notes.extractors.anchor_walker import AnchorWalkerExtractor
from study_notes.extractors.dotted_id import DottedIdExtractor
from study_notes.extractors.positional_verse import PositionalVerseExtractor
from study_notes.extractors.jet_bible import JetBibleExtractor

# String key used in SourceConfig.extractor -> class. A new extractor family
# registers itself here; sources.py never imports extractor classes directly.
REGISTRY = {
    "numeric_id": NumericIdExtractor,
    "anchor_walker": AnchorWalkerExtractor,
    "dotted_id": DottedIdExtractor,
    "positional_verse": PositionalVerseExtractor,
    "jet_bible": JetBibleExtractor,
}
