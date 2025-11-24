from fastapi import FastAPI
from pydantic import BaseModel

from symbios.backend.omega_gate import omega_gate
from symbios.backend.pose_lite import register_evidence


class Request(BaseModel):
    model: str
    input: dict
    output: dict
    context: dict


app = FastAPI(title="SymbiOS Ω-GATE + PoSE-Lite MVP")


@app.post("/symbios/ia/invoke")
def invoke_ia(req: Request):
    """Invoke the Omega Gate and optionally record evidence."""

    request_payload = req.model_dump()
    gate_result = omega_gate(request_payload)

    if gate_result["approved"]:
        register_evidence(request_payload, gate_result)

    return gate_result


@app.get("/")
def root():
    return {"status": "SymbiOS Ω-GATE + PoSE-Lite MVP"}
