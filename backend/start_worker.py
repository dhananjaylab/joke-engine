#!/usr/bin/env python3
"""
Start ARQ worker for background tasks.
Usage: python start_worker.py
"""
import asyncio
from arq import run_worker
from workers.settings import WorkerSettings

if __name__ == "__main__":
    print("Starting ARQ worker...")
    print("Available tasks:", WorkerSettings.functions)
    run_worker(WorkerSettings)