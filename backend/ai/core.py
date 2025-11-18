import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SymbiOS AI Calibrator")


class CalibrateRequest(BaseModel):
    payload: dict


@app.post("/calibrate")
def calibrate(body: CalibrateRequest):
    # Simple heuristic to keep the pipeline operational during development
    magnitude = len(str(body.payload))
    omega_score = max(0.0, min(1.0, magnitude / 10))
    recommendation = "ACCELERATE" if omega_score > 0.6 else "MONITOR"
    return {"omega_score": omega_score, "recommendation": recommendation}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
