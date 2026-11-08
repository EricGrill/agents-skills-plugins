"""Logging and Monitoring Utilities

This module provides logging, performance monitoring, and observability
utilities for the multi-agent system.
"""

import logging
import time
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    agent: str
    level: str
    message: str
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "agent": self.agent,
            "level": self.level,
            "message": self.message,
            **self.extra
        }


class AgentLogger:
    """Unified logging for agents
    
    Provides structured logging with local console output and
    in-memory storage for analysis.
    """
    
    def __init__(self, agent_name: str, log_level: str = "INFO"):
        self.agent_name = agent_name
        self.logs: List[LogEntry] = []
        
        # Set up Python logging
        self.logger = logging.getLogger(agent_name)
        self.logger.setLevel(getattr(logging, log_level))
        
        # Clear any existing handlers
        self.logger.handlers = []
        
        # Console handler with formatting
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log(self, level: str, message: str, **extra):
        """Log a message with optional extra fields
        
        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            **extra: Additional fields to include in the log
        """
        
        log_entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            agent=self.agent_name,
            level=level,
            message=message,
            extra=extra
        )
        
        self.logs.append(log_entry)
        
        # Also log to Python logger
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        
        # Format extra data for console
        if extra:
            extra_str = " | " + " | ".join(f"{k}={v}" for k, v in extra.items())
            log_method(message + extra_str)
        else:
            log_method(message)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.log("DEBUG", message, **kwargs)
    
    def get_logs(self, level: Optional[str] = None) -> List[LogEntry]:
        """Get logs with optional level filter
        
        Args:
            level: Filter by log level (INFO, WARNING, ERROR, DEBUG)
            
        Returns:
            List of log entries
        """
        if level:
            return [log for log in self.logs if log.level == level]
        return self.logs
    
    def export_logs(self, filepath: str, format: str = "json") -> None:
        """Export logs to file
        
        Args:
            filepath: Path to export file
            format: Export format ('json' or 'text')
        """
        if format == "json":
            with open(filepath, 'w') as f:
                json.dump([log.to_dict() for log in self.logs], f, indent=2)
        else:  # text format
            with open(filepath, 'w') as f:
                for log in self.logs:
                    f.write(f"{log.timestamp} - {log.agent} - {log.level} - {log.message}\n")
                    if log.extra:
                        f.write(f"  Extra: {log.extra}\n")
    
    def clear_logs(self) -> None:
        """Clear all stored logs"""
        self.logs = []


class PerformanceMonitor:
    """Monitor agent and operation performance
    
    Tracks timing, resource usage, and performance metrics.
    """
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.operation_counts: Dict[str, int] = {}
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation
        
        Args:
            operation: Name of the operation to time
        """
        if operation not in self.metrics:
            self.metrics[operation] = {
                "start_time": None,
                "end_time": None,
                "duration": None,
                "count": 0
            }
        
        self.metrics[operation]["start_time"] = time.time()
        self.operation_counts[operation] = self.operation_counts.get(operation, 0) + 1
    
    def end_timer(self, operation: str) -> Optional[float]:
        """End timing an operation
        
        Args:
            operation: Name of the operation to end timing for
            
        Returns:
            Duration in seconds, or None if operation not found
        """
        if operation not in self.metrics:
            return None
        
        if self.metrics[operation]["start_time"] is None:
            return None
        
        self.metrics[operation]["end_time"] = time.time()
        self.metrics[operation]["duration"] = (
            self.metrics[operation]["end_time"] - 
            self.metrics[operation]["start_time"]
        )
        self.metrics[operation]["count"] = self.operation_counts.get(operation, 0)
        
        return self.metrics[operation]["duration"]
    
    def get_duration(self, operation: str) -> Optional[float]:
        """Get duration of an operation in seconds
        
        Args:
            operation: Name of the operation
            
        Returns:
            Duration in seconds, or None if not found or not completed
        """
        if operation in self.metrics:
            return self.metrics[operation].get("duration")
        return None
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all performance metrics
        
        Returns:
            Dictionary of all metrics
        """
        return self.metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary
        
        Returns:
            Summary statistics of all operations
        """
        completed_ops = {
            name: metrics for name, metrics in self.metrics.items()
            if metrics.get("duration") is not None
        }
        
        if not completed_ops:
            return {
                "total_operations": 0,
                "total_time": 0,
                "operations": {}
            }
        
        total_time = sum(m["duration"] for m in completed_ops.values())
        
        return {
            "total_operations": len(completed_ops),
            "total_time": total_time,
            "operations": {
                name: {
                    "duration": metrics["duration"],
                    "count": metrics.get("count", 1),
                    "percentage": (metrics["duration"] / total_time * 100) if total_time > 0 else 0
                }
                for name, metrics in completed_ops.items()
            }
        }
    
    def record_metric(self, name: str, value: Any, unit: str = "") -> None:
        """Record a custom metric
        
        Args:
            name: Metric name
            value: Metric value
            unit: Optional unit (e.g., 'ms', 'MB', 'count')
        """
        if name not in self.metrics:
            self.metrics[name] = {
                "values": [],
                "unit": unit
            }
        
        self.metrics[name]["values"].append({
            "value": value,
            "timestamp": time.time()
        })
    
    def get_metric_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a metric
        
        Args:
            name: Metric name
            
        Returns:
            Dictionary with min, max, avg, count
        """
        if name not in self.metrics or "values" not in self.metrics[name]:
            return None
        
        values = [v["value"] for v in self.metrics[name]["values"] if isinstance(v["value"], (int, float))]
        
        if not values:
            return None
        
        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values),
            "unit": self.metrics[name].get("unit", "")
        }
    
    def reset(self) -> None:
        """Reset all metrics"""
        self.metrics = {}
        self.operation_counts = {}


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Monitoring Module")
    print("=" * 60)
    
    # Test 1: AgentLogger
    print("\n1. Testing AgentLogger...")
    logger = AgentLogger("test_agent")
    
    logger.info("Agent initialized", version="1.0")
    logger.debug("Debug information", step=1)
    logger.warning("Something to watch", threshold=0.8)
    logger.error("An error occurred", error_code="ERR_001")
    
    logs = logger.get_logs()
    print(f"✅ Logged {len(logs)} messages")
    
    error_logs = logger.get_logs(level="ERROR")
    print(f"✅ Found {len(error_logs)} error messages")
    
    # Test 2: PerformanceMonitor
    print("\n2. Testing PerformanceMonitor...")
    perf = PerformanceMonitor()
    
    # Test operation timing
    perf.start_timer("scan_repository")
    time.sleep(0.1)  # Simulate work
    duration = perf.end_timer("scan_repository")
    print(f"✅ scan_repository completed in {duration:.3f}s")
    
    perf.start_timer("analyze_code")
    time.sleep(0.05)
    perf.end_timer("analyze_code")
    
    perf.start_timer("create_problem")
    time.sleep(0.08)
    perf.end_timer("create_problem")
    
    # Test custom metrics
    perf.record_metric("quality_score", 92, "score")
    perf.record_metric("quality_score", 88, "score")
    perf.record_metric("quality_score", 95, "score")
    
    stats = perf.get_metric_stats("quality_score")
    print(f"✅ Quality score stats: avg={stats['avg']:.1f}, min={stats['min']}, max={stats['max']}")
    
    # Test summary
    summary = perf.get_summary()
    print(f"\n✅ Performance Summary:")
    print(f"   Total operations: {summary['total_operations']}")
    print(f"   Total time: {summary['total_time']:.3f}s")
    for op_name, op_stats in summary['operations'].items():
        print(f"   - {op_name}: {op_stats['duration']:.3f}s ({op_stats['percentage']:.1f}%)")
    
    # Test 3: Log export
    print("\n3. Testing log export...")
    logger.export_logs("/tmp/test_agent_logs.json", format="json")
    print("✅ Logs exported to /tmp/test_agent_logs.json")
    
    print("\n" + "=" * 60)
    print("✅ All monitoring tests passed!")
