import json
import time
from datetime import datetime
from typing import Any, Dict

import requests

URL = "http://localhost:8000/symbios/ia/invoke"


def run_fake_request(index: int) -> Dict[str, Any]:
    payload = {
        "model": "gpt-4o",
        "input": {"prompt": f"Responda a pergunta {index}"},
        "output": {"text": f"Resposta simulada {index}", "tokens": 10 + index},
        "context": {"expected_format": "text", "timestamp": datetime.utcnow().isoformat()},
    }
    response = requests.post(URL, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    results = []
    for i in range(5):
        results.append(run_fake_request(i))
        time.sleep(0.5)

    print(json.dumps(results, indent=2, ensure_ascii=False))
    print("Bench finalizado. Verifique evidence.json e pose_log.txt.")


if __name__ == "__main__":
    main()
