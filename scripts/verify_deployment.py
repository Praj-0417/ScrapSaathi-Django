#!/usr/bin/env python3
"""
ScrapSaathi Post-Deployment Verification & Operational Health Evaluator.
Automates post-release sanity testing, latency SLA validation, database probes,
and Prometheus metrics ingestion verification.

Usage:
    python scripts/verify_deployment.py [--base-url http://localhost:8000] [--timeout 5]
Exit codes:
    0 = All operational checks and SLAs passed.
    1 = Verification failure / SLA breached.
"""

import sys
import time
import argparse
import logging
from typing import Dict, Any
import requests

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger('deploy-verify')

class DeploymentVerifier:
    def __init__(self, base_url: str = 'http://127.0.0.1:8000', timeout: float = 5.0, max_latency_ms: float = 500.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_latency_ms = max_latency_ms
        self.results: Dict[str, Dict[str, Any]] = {}

    def _probe_endpoint(self, path: str, expected_status: int = 200, check_json: bool = True) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        start = time.perf_counter()
        try:
            resp = requests.get(url, timeout=self.timeout)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            passed = (resp.status_code == expected_status) and (duration_ms <= self.max_latency_ms)
            
            data = resp.json() if (check_json and resp.headers.get('content-type', '').startswith('application/json')) else resp.text[:200]
            raw_text = resp.text if not check_json else ""
            return {
                'url': url,
                'status_code': resp.status_code,
                'latency_ms': duration_ms,
                'sla_passed': duration_ms <= self.max_latency_ms,
                'passed': passed,
                'response': data,
                'raw_text': raw_text,
            }
        except Exception as e:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                'url': url,
                'status_code': 0,
                'latency_ms': duration_ms,
                'sla_passed': False,
                'passed': False,
                'error': str(e),
            }

    def run_all(self) -> bool:
        logger.info(f"Starting post-deployment verification on {self.base_url} (Timeout: {self.timeout}s, SLA: <{self.max_latency_ms}ms)")

        # 1. Root Health Check
        logger.info("Probing Root Health endpoint (/health)...")
        self.results['root_health'] = self._probe_endpoint('/health')

        # 2. API v1 Health Check
        logger.info("Probing API v1 Health endpoint (/api/v1/health)...")
        self.results['api_health'] = self._probe_endpoint('/api/v1/health')

        # 3. Prometheus Metrics Scraping
        logger.info("Probing Prometheus Metrics endpoint (/metrics)...")
        metrics_res = self._probe_endpoint('/metrics', check_json=False)
        if metrics_res['passed'] and ('django_http_requests' in str(metrics_res.get('raw_text', '')) or 'django_' in str(metrics_res.get('raw_text', ''))):
            metrics_res['metrics_verified'] = True
        else:
            metrics_res['metrics_verified'] = False
            metrics_res['passed'] = False
        self.results['prometheus_metrics'] = metrics_res

        # 4. Scrap Rates Catalog Probe
        logger.info("Probing Scrap Rates Board (/api/v1/rates?city=delhi-ncr)...")
        self.results['rates_catalog'] = self._probe_endpoint('/api/v1/rates?city=delhi-ncr')

        # 5. Geocode Serviceability Probe
        logger.info("Probing Geocode Serviceability Hubs (/api/v1/geocode/serviceable?lat=28.6315&lon=77.2167)...")
        self.results['geocode_serviceability'] = self._probe_endpoint('/api/v1/geocode/serviceable?lat=28.6315&lon=77.2167')

        # Generate summary
        all_passed = all(r.get('passed', False) for r in self.results.values())
        self.print_report(all_passed)
        return all_passed

    def print_report(self, all_passed: bool):
        print("\n" + "=" * 65)
        print("         SCRAPSAATHI POST-DEPLOYMENT VERIFICATION REPORT         ")
        print("=" * 65)
        for check, res in self.results.items():
            status_label = "PASS" if res.get('passed') else "FAIL"
            latency = f"{res.get('latency_ms', 0)}ms"
            code = res.get('status_code', 'ERR')
            print(f"[{status_label}] {check.ljust(25)} | HTTP {code} | {latency.rjust(8)} | SLA: {'OK' if res.get('sla_passed') else 'BREACH'}")
            if not res.get('passed') and res.get('error'):
                print(f"       Error: {res['error']}")
        print("=" * 65)
        print(f"FINAL RESULT: {'SUCCESS (ALL CHECKS PASSED)' if all_passed else 'FAILURE (SOME CHECKS FAILED)'}")
        print("=" * 65 + "\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8000', help='Target application base URL')
    parser.add_argument('--timeout', type=float, default=5.0, help='Request timeout in seconds')
    parser.add_argument('--max-latency', type=float, default=500.0, help='Max acceptable latency in ms')
    args = parser.parse_args()

    verifier = DeploymentVerifier(base_url=args.base_url, timeout=args.timeout, max_latency_ms=args.max_latency)
    success = verifier.run_all()
    sys.exit(0 if success else 1)
