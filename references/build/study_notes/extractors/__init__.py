from study_notes.extractors.numeric_id import NumericIdExtractor
from study_notes.extractors.anchor_walker import AnchorWalkerExtractor

# String key used in SourceConfig.extractor -> class. A new extractor family
# registers itself here; sources.py never imports extractor classes directly.
REGISTRY = {
    "numeric_id": NumericIdExtractor,
    "anchor_walker": AnchorWalkerExtractor,
}
