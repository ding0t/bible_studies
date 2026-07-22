"""The contract every extractor family implements.

A source (an EPUB) is handed to exactly one extractor class, configured by
its SourceConfig (see ../sources.py). The extractor's only job is to walk
that EPUB's unzipped tree and produce an ExtractionResult -- it must never
touch the database directly. That split is what lets a 5th study Bible be
added as pure configuration if it fits an existing family, or as one new
extractor module if it doesn't, without either path touching writer.py.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from study_notes.models import ExtractionResult


@dataclass
class SourceConfig:
    """Declarative description of one study-Bible EPUB. Extractor-family-specific
    fields live in `extra` rather than growing this class per-family -- keeps the
    registry (sources.py) readable regardless of how many families exist."""
    work_id: str
    epub_path: Path
    title: str
    publisher: str
    year: int
    license_tier: str
    extractor: str          # dotted key into the registry in extractors/__init__.py
    extra: dict = field(default_factory=dict)


class BaseExtractor(ABC):
    def __init__(self, config: SourceConfig, unzipped_root: Path, image_dir: Path):
        self.config = config
        self.root = unzipped_root
        self.image_dir = image_dir

    @abstractmethod
    def extract(self) -> ExtractionResult:
        ...
