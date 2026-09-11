import time
import os
from typing import Dict, List
import psutil

class MetricsCollector:
    """
    In-memory metrics collector producing standard Prometheus exposition format.
    Conforms to PRD Section 6.2:
    - Latency per component & total
    - Requests per route (rag, kag, hybrid, escalated, direct)
    - Errors per dependency (ollama, chroma, n8n)
    - Resource usage (CPU, RAM) via psutil
    """
    def __init__(self):
        self.routes = ["rag", "kag", "hybrid", "escalated", "direct"]
        self.requests_total: Dict[str, int] = {r: 0 for r in self.routes}
        self.errors_total: Dict[str, int] = {"ollama": 0, "chroma": 0, "n8n": 0}
        self.component_latencies: Dict[str, List[float]] = {
            "llm": [],
            "retrieval": [],
            "rerank": [],
            "total": []
        }
        self.process = psutil.Process(os.getpid())

    def record_request(self, route: str, total_latency_ms: float):
        if route in self.requests_total:
            self.requests_total[route] += 1
        else:
            self.requests_total[route] = 1
        self.record_latency("total", total_latency_ms)

    def record_error(self, dependency: str):
        if dependency in self.errors_total:
            self.errors_total[dependency] += 1
        else:
            self.errors_total[dependency] = 1

    def record_latency(self, component: str, latency_ms: float):
        if component in self.component_latencies:
            self.component_latencies[component].append(latency_ms)
            # Keep last 100 values to conserve memory
            if len(self.component_latencies[component]) > 100:
                self.component_latencies[component].pop(0)

    def generate_prometheus_metrics(self) -> str:
        lines = []

        # 1. Total Requests by Route
        lines.append("# HELP supportsense_requests_total Total number of chat requests processed by route")
        lines.append("# TYPE supportsense_requests_total counter")
        for route, count in sorted(self.requests_total.items()):
            lines.append(f'supportsense_requests_total{{route="{route}"}} {count}')

        # 2. Total Errors by Dependency
        lines.append("\n# HELP supportsense_errors_total Total errors encountered by external dependency")
        lines.append("# TYPE supportsense_errors_total counter")
        for dep, count in sorted(self.errors_total.items()):
            lines.append(f'supportsense_errors_total{{dependency="{dep}"}} {count}')

        # 3. Average Latency by Component
        lines.append("\n# HELP supportsense_component_latency_ms Average latency in milliseconds per component")
        lines.append("# TYPE supportsense_component_latency_ms gauge")
        for comp, vals in sorted(self.component_latencies.items()):
            avg = round(sum(vals) / len(vals), 2) if vals else 0.0
            lines.append(f'supportsense_component_latency_ms{{component="{comp}"}} {avg}')

        # 4. Resource Usage
        try:
            cpu_pct = psutil.cpu_percent(interval=None)
            mem_info = self.process.memory_info()
            mem_mb = round(mem_info.rss / 1024 / 1024, 2)
        except Exception:
            cpu_pct = 0.0
            mem_mb = 0.0

        lines.append("\n# HELP supportsense_process_cpu_percent Process CPU utilization percentage")
        lines.append("# TYPE supportsense_process_cpu_percent gauge")
        lines.append(f"supportsense_process_cpu_percent {cpu_pct}")

        lines.append("\n# HELP supportsense_process_memory_mb Process Resident Set Size (RSS) memory in megabytes")
        lines.append("# TYPE supportsense_process_memory_mb gauge")
        lines.append(f"supportsense_process_memory_mb {mem_mb}")

        return "\n".join(lines) + "\n"

# Global singleton metrics instance
metrics = MetricsCollector()
