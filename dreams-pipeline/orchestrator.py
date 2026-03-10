"""
DREAMS Pipeline — Orchestrator
===============================
Minimal entry point: ingests a dataset CSV through the pipeline
and builds the full cognitive graph for each user.

Usage:
    python orchestrator.py
    python orchestrator.py --csv path/to/dataset.csv --images path/to/images/
"""

import os
import csv
import argparse
import logging
from datetime import datetime

from ingestion.pipeline import process_memory
from storage.metadata_store import MetadataStore
from storage.vector_store import VectorStore
from storage.graph_store import GraphStore
from graph.builder import GraphBuilder

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def ingest_dataset(csv_path, images_dir, metadata_store, vector_store):
    """Read CSV, run extractors on each row, persist to stores."""
    memories = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            image_path = os.path.join(images_dir, row['image_filename'])
            try:
                timestamp = datetime.strptime(row['date'].strip(), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                logger.warning("Skipping row %s — bad date", row['id'])
                continue

            logger.info("Processing row %s", row['id'])
            memory = process_memory(
                image_path=image_path,
                user_id=row['user_id'],
                timestamp=timestamp,
                caption=row['caption'],
                memory_id=f"memory_{row['id']}"
            )

            metadata_store.save_memory(memory)
            vector_store.insert_memory(memory)
            memories.append(memory)

    return memories


def build_graphs(memories, graph_store, vector_store):
    """Group memories by user and build their cognitive graphs."""
    builder = GraphBuilder(graph_store, vector_store)
    users = set(m.user_id for m in memories)

    for user_id in users:
        user_memories = [m for m in memories if m.user_id == user_id]
        logger.info("Building graph for %s (%d memories)", user_id, len(user_memories))
        builder.build_for_user(user_id, user_memories)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description='DREAMS Pipeline Orchestrator')
    parser.add_argument('--csv', default=os.path.join(base_dir, 'data', 'synthetic-data', 'dataset.csv'))
    parser.add_argument('--images', default=os.path.join(base_dir, 'data', 'synthetic-data', 'images'))
    args = parser.parse_args()

    metadata_store = MetadataStore()
    vector_store = VectorStore()
    graph_store = GraphStore()

    memories = ingest_dataset(args.csv, args.images, metadata_store, vector_store)
    logger.info("Ingested %d memories", len(memories))

    build_graphs(memories, graph_store, vector_store)
    logger.info("Pipeline complete ✓")


if __name__ == '__main__':
    main()
