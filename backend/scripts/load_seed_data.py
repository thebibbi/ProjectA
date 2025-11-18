#!/usr/bin/env python3
"""
Load seed data into Safety Graph Twin database.

This script loads sample HARA, FMEA, Requirements, and Tests data
to populate the knowledge graph for demonstration and testing.

Usage:
    python scripts/load_seed_data.py [--api-url http://localhost:8000]
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SeedDataLoader:
    """Load seed data into the Safety Graph Twin API."""

    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Initialize loader.

        Args:
            api_url: Base URL of the Safety Graph Twin API
        """
        self.api_url = api_url.rstrip("/")
        self.seed_dir = Path(__file__).parent.parent / "data" / "seed"

    def check_api_health(self) -> bool:
        """
        Check if API is healthy and reachable.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response.raise_for_status()

            health = response.json()
            logger.info(f"✓ API health check: {health['status']}")

            # Check database health
            db_response = requests.get(f"{self.api_url}/health/db", timeout=5)
            db_health = db_response.json()

            if db_health["status"] == "healthy":
                logger.info(f"✓ Database health check: {db_health['status']}")
                return True
            else:
                logger.error(f"✗ Database unhealthy: {db_health.get('message')}")
                return False

        except requests.RequestException as e:
            logger.error(f"✗ API health check failed: {e}")
            return False

    def load_json_file(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON file from seed directory.

        Args:
            filename: Name of JSON file

        Returns:
            Parsed JSON data

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        file_path = self.seed_dir / filename
        logger.info(f"Loading {filename}...")

        with open(file_path, "r") as f:
            return json.load(f)

    def import_hara_data(self) -> bool:
        """
        Import HARA data (hazards, scenarios, safety goals).

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 70)
        logger.info("Importing HARA Data")
        logger.info("=" * 70)

        try:
            data = self.load_json_file("hara_data.json")

            response = requests.post(
                f"{self.api_url}/import/hara",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"✓ HARA import successful:")
            logger.info(f"  - Hazards created: {result['data']['hazards_created']}")
            logger.info(f"  - Scenarios created: {result['data']['scenarios_created']}")
            logger.info(f"  - Safety goals created: {result['data']['safety_goals_created']}")
            logger.info(f"  - Relationships created: {result['data']['relationships_created']}")

            return True

        except requests.HTTPError as e:
            logger.error(f"✗ HARA import failed (HTTP {e.response.status_code}):")
            try:
                error_detail = e.response.json()
                logger.error(f"  {error_detail}")
            except json.JSONDecodeError:
                logger.error(f"  {e.response.text}")
            return False

        except Exception as e:
            logger.error(f"✗ HARA import failed: {e}")
            return False

    def import_fmea_data(self) -> bool:
        """
        Import FMEA data (components, failure modes, FMEA entries).

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 70)
        logger.info("Importing FMEA Data")
        logger.info("=" * 70)

        try:
            data = self.load_json_file("fmea_data.json")

            response = requests.post(
                f"{self.api_url}/import/fmea",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"✓ FMEA import successful:")
            logger.info(f"  - Components created: {result['data']['components_created']}")
            logger.info(f"  - Failure modes created: {result['data']['failure_modes_created']}")
            logger.info(f"  - FMEA entries created: {result['data']['fmea_entries_created']}")
            logger.info(f"  - Relationships created: {result['data']['relationships_created']}")

            return True

        except requests.HTTPError as e:
            logger.error(f"✗ FMEA import failed (HTTP {e.response.status_code}):")
            try:
                error_detail = e.response.json()
                logger.error(f"  {error_detail}")
            except json.JSONDecodeError:
                logger.error(f"  {e.response.text}")
            return False

        except Exception as e:
            logger.error(f"✗ FMEA import failed: {e}")
            return False

    def import_requirements_data(self) -> bool:
        """
        Import requirements data (FSRs, TSRs).

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 70)
        logger.info("Importing Requirements Data")
        logger.info("=" * 70)

        try:
            data = self.load_json_file("requirements_data.json")

            response = requests.post(
                f"{self.api_url}/import/requirements",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"✓ Requirements import successful:")
            logger.info(f"  - FSRs created: {result['data']['fsrs_created']}")
            logger.info(f"  - TSRs created: {result['data']['tsrs_created']}")
            logger.info(f"  - Components created: {result['data']['components_created']}")
            logger.info(f"  - Relationships created: {result['data']['relationships_created']}")

            return True

        except requests.HTTPError as e:
            logger.error(f"✗ Requirements import failed (HTTP {e.response.status_code}):")
            try:
                error_detail = e.response.json()
                logger.error(f"  {error_detail}")
            except json.JSONDecodeError:
                logger.error(f"  {e.response.text}")
            return False

        except Exception as e:
            logger.error(f"✗ Requirements import failed: {e}")
            return False

    def import_tests_data(self) -> bool:
        """
        Import test cases data.

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 70)
        logger.info("Importing Tests Data")
        logger.info("=" * 70)

        try:
            data = self.load_json_file("tests_data.json")

            response = requests.post(
                f"{self.api_url}/import/tests",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"✓ Tests import successful:")
            logger.info(f"  - Test cases created: {result['data']['test_cases_created']}")
            logger.info(f"  - Relationships created: {result['data']['relationships_created']}")

            return True

        except requests.HTTPError as e:
            logger.error(f"✗ Tests import failed (HTTP {e.response.status_code}):")
            try:
                error_detail = e.response.json()
                logger.error(f"  {error_detail}")
            except json.JSONDecodeError:
                logger.error(f"  {e.response.text}")
            return False

        except Exception as e:
            logger.error(f"✗ Tests import failed: {e}")
            return False

    def get_statistics(self) -> bool:
        """
        Get and display database statistics after import.

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 70)
        logger.info("Database Statistics")
        logger.info("=" * 70)

        try:
            response = requests.get(f"{self.api_url}/analytics/statistics", timeout=10)
            response.raise_for_status()

            result = response.json()
            stats = result["data"]

            summary = stats.get("summary", {})
            logger.info(f"Summary:")
            logger.info(f"  - Total nodes: {summary.get('total_nodes', 0)}")
            logger.info(f"  - Total relationships: {summary.get('total_relationships', 0)}")
            logger.info(f"  - Total hazards: {summary.get('total_hazards', 0)}")
            logger.info(f"  - Verified hazards: {summary.get('verified_hazards', 0)}")
            logger.info(f"  - Coverage: {summary.get('coverage_percentage', 0):.1f}%")

            node_counts = stats.get("node_counts", {})
            if node_counts:
                logger.info(f"\nNode counts:")
                for label, count in sorted(node_counts.items()):
                    logger.info(f"  - {label}: {count}")

            return True

        except Exception as e:
            logger.error(f"✗ Failed to get statistics: {e}")
            return False

    def load_all(self) -> bool:
        """
        Load all seed data in correct order.

        Returns:
            True if all imports successful, False otherwise
        """
        logger.info("=" * 70)
        logger.info("Safety Graph Twin - Seed Data Loader")
        logger.info("=" * 70)

        # Check API health
        if not self.check_api_health():
            logger.error("API is not healthy. Cannot proceed with import.")
            return False

        # Import data in dependency order
        success = True

        # 1. HARA (no dependencies)
        if not self.import_hara_data():
            success = False

        # 2. FMEA (no dependencies)
        if not self.import_fmea_data():
            success = False

        # 3. Requirements (depends on HARA safety goals and FMEA components)
        if not self.import_requirements_data():
            success = False

        # 4. Tests (depends on Requirements TSRs and Components)
        if not self.import_tests_data():
            success = False

        # Get final statistics
        self.get_statistics()

        logger.info("=" * 70)
        if success:
            logger.info("✓ All seed data loaded successfully!")
        else:
            logger.warning("⚠ Some imports failed. Check logs above for details.")
        logger.info("=" * 70)

        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Load seed data into Safety Graph Twin database"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL of the Safety Graph Twin API (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    loader = SeedDataLoader(api_url=args.api_url)
    success = loader.load_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
