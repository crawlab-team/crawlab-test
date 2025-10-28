"""
Specification Finder Module

This module provides functionality to find, search, and list test specifications.
"""

import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional


class SpecFinder:
    """Finds and searches test specifications"""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize SpecFinder

        Args:
            base_dir: Base directory for tests (defaults to workspace root)
        """
        if base_dir is None:
            # First, check if current working directory has specs/ directory
            # This handles pip-installed packages where specs/ is in the repo root
            cwd = Path.cwd()
            if (cwd / "specs").exists():
                base_dir = cwd
            else:
                # Fall back to calculating from package location (development mode)
                # From crawlab_test/core/spec_finder.py, go up 2 levels to repo root
                base_dir = Path(__file__).parent.parent.parent

        self.base_dir = Path(base_dir)
        self.specs_dir = self.base_dir / "specs"

        if not self.specs_dir.exists():
            raise ValueError(f"Specs directory not found: {self.specs_dir}")

    def list_specs(self, categories: Optional[List[str]] = None) -> List[Dict]:
        """
        List all available test specifications

        Args:
            categories: Optional list of category filters (e.g., ['ui', 'cluster'])

        Returns:
            List of spec dictionaries with metadata
        """
        specs = []

        # Collect search directories based on categories
        if categories:
            search_dirs = []
            for category in categories:
                search_dir = self.specs_dir / category
                if search_dir.exists():
                    search_dirs.append(search_dir)
                else:
                    print(f"Warning: Category '{category}' not found")

            if not search_dirs:
                print("No valid categories found")
                return []
        else:
            search_dirs = [self.specs_dir]

        # Gather specs from all search directories
        for search_dir in search_dirs:
            for spec_file in search_dir.rglob("*.md"):
                if spec_file.name in ["README.md", "TEMPLATE.md"]:
                    continue

                metadata = self._parse_spec_metadata(spec_file)

                # Extract spec ID from filename (e.g., UI-001, INF-004, DEP-002)
                spec_id_match = re.search(r"([A-Z]+)-(\d+)", spec_file.stem)
                spec_id = spec_id_match.group(0) if spec_id_match else None

                specs.append(
                    {
                        "id": spec_id,
                        "file": str(spec_file.relative_to(self.base_dir)),
                        "category": spec_file.parent.name,
                        "title": metadata.get("title", spec_file.stem),
                        "priority": metadata.get("priority", "unknown"),
                        "duration": metadata.get("duration", "unknown"),
                        "complexity": metadata.get("complexity", "unknown"),
                    }
                )

        return sorted(specs, key=lambda x: (x["category"], x["priority"], x["title"]))

    def find_spec_by_query(self, query: str, threshold: float = 0.5) -> List[Dict]:
        """
        Find specs by ID or fuzzy search

        Args:
            query: Search query (spec ID or search terms)
            threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of matching specs, sorted by relevance
        """
        all_specs = self.list_specs()

        # First, try exact ID match
        id_pattern = re.compile(r"^([A-Z]+)-?(\d+)$", re.IGNORECASE)
        id_match = id_pattern.match(query.strip())

        if id_match:
            # Normalize ID format (e.g., "ui001" -> "UI-001")
            prefix = id_match.group(1).upper()
            number = id_match.group(2).zfill(3)
            normalized_id = f"{prefix}-{number}"

            # Look for exact ID match
            exact_matches = [s for s in all_specs if s.get("id") == normalized_id]
            if exact_matches:
                return exact_matches

            # Try without zero-padding for backward compatibility
            alt_id = f"{prefix}-{int(number)}"
            alt_matches = [s for s in all_specs if s.get("id") == alt_id]
            if alt_matches:
                return alt_matches

        # Fuzzy search across multiple fields
        scored_specs = []
        for spec in all_specs:
            max_score = 0.0

            # Check ID
            if spec.get("id"):
                score = self._fuzzy_match_score(query, spec["id"])
                max_score = max(max_score, score)

            # Check filename
            filename = Path(spec["file"]).stem
            score = self._fuzzy_match_score(query, filename)
            max_score = max(max_score, score)

            # Check title
            if spec.get("title"):
                score = self._fuzzy_match_score(query, spec["title"])
                max_score = max(max_score, score)

            # Check category
            if spec.get("category"):
                score = self._fuzzy_match_score(query, spec["category"])
                max_score = max(max_score, score * 0.7)  # Lower weight for category

            if max_score >= threshold:
                scored_specs.append((max_score, spec))

        # Sort by score (highest first)
        scored_specs.sort(key=lambda x: x[0], reverse=True)

        return [spec for score, spec in scored_specs]

    def find_spec_by_path(self, spec_path: str) -> Optional[Path]:
        """
        Resolve a spec path to an absolute path

        Args:
            spec_path: Relative or absolute path to spec file

        Returns:
            Absolute Path to spec file, or None if not found
        """
        spec_file = Path(spec_path)

        if not spec_file.is_absolute():
            spec_file = self.base_dir / spec_path

        if spec_file.exists():
            return spec_file

        return None

    def _fuzzy_match_score(self, query: str, text: str) -> float:
        """
        Calculate fuzzy match score between query and text

        Args:
            query: Search query
            text: Text to match against

        Returns:
            Similarity score (0.0-1.0)
        """
        query_lower = query.lower()
        text_lower = text.lower()

        # Exact match gets highest score
        if query_lower == text_lower:
            return 1.0

        # Check if query is contained in text
        if query_lower in text_lower:
            return 0.9

        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, query_lower, text_lower).ratio()

    def _parse_spec_metadata(self, spec_file: Path) -> Dict:
        """
        Extract metadata from test specification

        Args:
            spec_file: Path to spec file

        Returns:
            Dictionary of metadata
        """
        metadata = {}

        try:
            with open(spec_file) as f:
                content = f.read()

            # Extract title from first heading
            title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
            if title_match:
                metadata["title"] = title_match.group(1)

            # Extract metadata section
            metadata_section = re.search(r"## Metadata\s*\n(.*?)\n## ", content, re.DOTALL)
            if metadata_section:
                for line in metadata_section.group(1).split("\n"):
                    if line.startswith("- **"):
                        match = re.search(r"- \*\*(.+?)\*\*:\s*(.+)", line)
                        if match:
                            key = match.group(1).lower().replace(" ", "_")
                            value = match.group(2).strip()
                            metadata[key] = value

        except Exception as e:
            print(f"Warning: Could not parse metadata from {spec_file}: {e}")

        return metadata
