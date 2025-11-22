#!/usr/bin/env python3
"""
Metrics Collector - Prometheus Exporter

Coleta métricas do MatVerse e expõe em formato Prometheus para
observabilidade e decisões autônomas.

Métricas coletadas:
- Ω-Score (omega_score_current)
- Ψ-Index (psi_index_current)
- β Antifragile (beta_antifragile_current)
- CPU/Memory usage
- Latency histogram
- Throughput

Author: MatVerse Team
Version: 1.0.0
Date: 2025-11-22
"""

import time
import psutil
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading


@dataclass
class MetricPoint:
    """Ponto único de métrica com timestamp"""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metric_type: str = "gauge"  # gauge, counter, histogram


class MetricsCollector:
    """
    Coletor de métricas para MatVerse com export Prometheus

    Coleta métricas em tempo real e as mantém em memória para
    consulta rápida pelo Decision Engine (<10ms).
    """

    def __init__(
        self,
        collection_interval: float = 1.0,  # segundos
        retention_points: int = 3600,       # 1h de dados
    ):
        self.collection_interval = collection_interval
        self.retention_points = retention_points

        # Armazenamento de métricas (thread-safe)
        self._lock = threading.RLock()
        self._metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=retention_points)
        )

        # Cache de última leitura
        self._last_values: Dict[str, float] = {}

        # Thread de coleta automática
        self._collection_thread: Optional[threading.Thread] = None
        self._stop_collection = threading.Event()

    def start_auto_collection(self):
        """Inicia coleta automática em background"""
        if self._collection_thread and self._collection_thread.is_alive():
            return

        self._stop_collection.clear()
        self._collection_thread = threading.Thread(
            target=self._auto_collect_loop,
            daemon=True
        )
        self._collection_thread.start()

    def stop_auto_collection(self):
        """Para coleta automática"""
        self._stop_collection.set()
        if self._collection_thread:
            self._collection_thread.join(timeout=2.0)

    def _auto_collect_loop(self):
        """Loop de coleta automática"""
        while not self._stop_collection.is_set():
            self.collect_system_metrics()
            time.sleep(self.collection_interval)

    def record_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        metric_type: str = "gauge"
    ):
        """
        Registra uma métrica

        Args:
            name: Nome da métrica (ex: "omega_score")
            value: Valor numérico
            labels: Labels opcionais
            metric_type: Tipo (gauge, counter, histogram)
        """
        labels = labels or {}
        metric_key = self._make_key(name, labels)

        point = MetricPoint(
            name=name,
            value=value,
            labels=labels,
            metric_type=metric_type
        )

        with self._lock:
            self._metrics[metric_key].append(point)
            self._last_values[metric_key] = value

    def get_current_value(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None,
        default: float = 0.0
    ) -> float:
        """Obtém valor mais recente de uma métrica"""
        metric_key = self._make_key(name, labels or {})

        with self._lock:
            return self._last_values.get(metric_key, default)

    def get_metric_history(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None,
        limit: int = 100
    ) -> List[MetricPoint]:
        """Obtém histórico de uma métrica"""
        metric_key = self._make_key(name, labels or {})

        with self._lock:
            if metric_key not in self._metrics:
                return []

            history = list(self._metrics[metric_key])
            return history[-limit:] if limit else history

    def collect_system_metrics(self):
        """Coleta métricas do sistema operacional"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1) / 100.0
        self.record_metric("system_cpu_usage", cpu_percent)

        # Memória
        mem = psutil.virtual_memory()
        self.record_metric("system_memory_usage", mem.percent / 100.0)
        self.record_metric("system_memory_available_mb", mem.available / 1024 / 1024)

        # Disco
        disk = psutil.disk_usage('/')
        self.record_metric("system_disk_usage", disk.percent / 100.0)

        # Network (se disponível)
        try:
            net = psutil.net_io_counters()
            self.record_metric("system_network_bytes_sent", net.bytes_sent, metric_type="counter")
            self.record_metric("system_network_bytes_recv", net.bytes_recv, metric_type="counter")
        except Exception:
            pass

    def export_prometheus(self) -> str:
        """
        Exporta métricas no formato Prometheus

        Formato:
        # HELP metric_name Descrição
        # TYPE metric_name gauge
        metric_name{label="value"} 0.95 1234567890
        """
        lines = []
        seen_names = set()

        with self._lock:
            for metric_key, history in self._metrics.items():
                if not history:
                    continue

                latest = history[-1]

                # Header (uma vez por métrica)
                if latest.name not in seen_names:
                    lines.append(f"# HELP {latest.name} MatVerse metric")
                    lines.append(f"# TYPE {latest.name} {latest.metric_type}")
                    seen_names.add(latest.name)

                # Labels
                labels_str = ""
                if latest.labels:
                    labels_parts = [f'{k}="{v}"' for k, v in latest.labels.items()]
                    labels_str = "{" + ",".join(labels_parts) + "}"

                # Métrica com timestamp
                timestamp_ms = int(latest.timestamp * 1000)
                lines.append(f"{latest.name}{labels_str} {latest.value} {timestamp_ms}")

        return "\n".join(lines) + "\n"

    def get_snapshot(self) -> Dict[str, float]:
        """Obtém snapshot de todas as métricas atuais"""
        with self._lock:
            return self._last_values.copy()

    def _make_key(self, name: str, labels: Dict[str, str]) -> str:
        """Cria chave única para métrica + labels"""
        if not labels:
            return name

        labels_sorted = sorted(labels.items())
        labels_str = ",".join(f"{k}={v}" for k, v in labels_sorted)
        return f"{name}{{{labels_str}}}"

    def clear(self):
        """Limpa todas as métricas"""
        with self._lock:
            self._metrics.clear()
            self._last_values.clear()


# === CLASSE DE INTEGRAÇÃO COM MATVERSE ===

class MatVerseMetricsCollector(MetricsCollector):
    """
    Coletor especializado para métricas do MatVerse Ω-S

    Adiciona métricas específicas do ecossistema:
    - omega_score_current
    - psi_index_current
    - beta_antifragile_current
    - quantum_states_count
    - governance_frequency_hz
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Inicializa métricas específicas do MatVerse
        self.record_metric("omega_score_current", 0.0)
        self.record_metric("psi_index_current", 0.0)
        self.record_metric("beta_antifragile_current", 0.0)
        self.record_metric("quantum_states_count", 46080)
        self.record_metric("governance_frequency_hz", 50.0)
        self.record_metric("ip_artifacts_protected", 154)

    def update_matverse_metrics(
        self,
        omega_score: float,
        psi_index: float,
        beta_antifragile: float,
        latency_ms: Optional[float] = None,
        throughput: Optional[float] = None
    ):
        """Atualiza métricas principais do MatVerse"""
        self.record_metric("omega_score_current", omega_score)
        self.record_metric("psi_index_current", psi_index)
        self.record_metric("beta_antifragile_current", beta_antifragile)

        if latency_ms is not None:
            self.record_metric("latency_ms", latency_ms, metric_type="histogram")

        if throughput is not None:
            self.record_metric("throughput_rps", throughput)


# === FUNÇÕES DE TESTE E DEMO ===

def demo_metrics_collector():
    """Demonstração do MetricsCollector"""
    print("=" * 80)
    print("📊 METRICS COLLECTOR - DEMONSTRAÇÃO")
    print("=" * 80)

    collector = MatVerseMetricsCollector(collection_interval=0.5)

    # Inicia coleta automática
    print("\n🚀 Iniciando coleta automática...")
    collector.start_auto_collection()

    # Simula atualização de métricas do MatVerse
    import random
    for i in range(5):
        omega = 0.90 + random.uniform(0, 0.08)
        psi = 0.95 + random.uniform(0, 0.04)
        beta = 1.10 + random.uniform(0, 0.15)
        latency = 30 + random.uniform(0, 50)
        throughput = 1500 + random.uniform(-300, 300)

        collector.update_matverse_metrics(omega, psi, beta, latency, throughput)

        print(f"\n📈 Update {i+1}:")
        print(f"   Ω={omega:.3f}, Ψ={psi:.3f}, β={beta:.3f}")
        print(f"   Latency={latency:.1f}ms, Throughput={throughput:.0f}rps")

        time.sleep(0.6)

    # Snapshot
    print("\n📸 Snapshot atual:")
    snapshot = collector.get_snapshot()
    for key, value in sorted(snapshot.items()):
        if 'system' in key or 'omega' in key or 'psi' in key or 'beta' in key:
            print(f"   {key}: {value:.3f}")

    # Export Prometheus
    print("\n📤 Export Prometheus (primeiras 15 linhas):")
    prom_output = collector.export_prometheus()
    lines = prom_output.split('\n')[:15]
    for line in lines:
        print(f"   {line}")

    # Para coleta
    collector.stop_auto_collection()

    print("\n" + "=" * 80)
    print("✅ Demonstração concluída!")
    print("=" * 80)


if __name__ == "__main__":
    demo_metrics_collector()
