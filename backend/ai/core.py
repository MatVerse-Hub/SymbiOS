#!/usr/bin/env python3
"""
SymbiOS Core: Ω-Calibration Engine
Quantifies risk antifrágil + Monte Carlo validation
"""

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from scipy.stats import norm
import json

app = FastAPI()

class CalibrationRequest(BaseModel):
    context: str
    human_confidence: float  # 0-1
    risk_tolerance: float    # 0-1

class CalibrationResponse(BaseModel):
    omega_score: float
    cvar_95: float
    recommendation: str
    monte_carlo_runs: int
    probability_success: float

def monte_carlo_simulation(human_confidence: float, risk_tolerance: float, n_runs: int = 10000):
    """
    Simula 10k cenários de decisão sob incerteza.
    Retorna distribuição de resultados + estatísticas.
    """
    # Simular retornos (payoffs) com ruído
    base_return = human_confidence
    volatility = (1 - risk_tolerance) * 0.5  # maior tolerância = menor vol
    
    results = np.random.normal(
        loc=base_return,
        scale=volatility,
        size=n_runs
    )
    
    # Clamp to [0, 1]
    results = np.clip(results, 0, 1)
    
    return results

def quantify_cvar(results: np.ndarray, confidence_level: float = 0.95):
    """
    Calcula Conditional Value at Risk (CVaR) no percentil 95.
    Mede perda esperada no pior caso.
    """
    var_threshold = np.percentile(results, (1 - confidence_level) * 100)
    cvar = np.mean(results[results <= var_threshold])
    return cvar

def compute_omega_score(human_confidence: float, risk_tolerance: float, results: np.ndarray):
    """
    Ω-Score = medida de antifragilidade
    Quanto o sistema ganha com estresse?
    
    Formula: Ω = (E[retorno] - CVaR_95) / E[retorno]
    """
    mean_return = np.mean(results)
    cvar = quantify_cvar(results)
    
    if mean_return < 1e-6:  # evitar divisão por zero
        omega = 0.85
    else:
        # Ganho sob estresse: quanto a média supera o pior caso
        omega = 1 - (cvar / mean_return) * 0.5
    
    # Bonus de confiança humana + tolerância a risco
    omega = min(1.0, omega * (0.5 + 0.5 * human_confidence) * (1 + 0.2 * risk_tolerance))
    
    return max(0.5, omega)  # Floor at 0.5

def recommend_action(omega_score: float, cvar: float):
    """
    Ω-GATE logic: Decide based on antifrágil metric.
    """
    if omega_score >= 0.85 and cvar < 0.02:
        return "ACCELERATE"
    elif omega_score >= 0.70:
        return "MONITOR"
    else:
        return "PAUSE"

@app.post("/calibrate", response_model=CalibrationResponse)
async def calibrate(request: CalibrationRequest):
    """
    Endpoint principal: calibra decisão humana com IA.
    """
    # Validação
    if not (0 <= request.human_confidence <= 1):
        request.human_confidence = max(0, min(1, request.human_confidence))
    if not (0 <= request.risk_tolerance <= 1):
        request.risk_tolerance = max(0, min(1, request.risk_tolerance))
    
    # Monte Carlo
    n_runs = 10000
    results = monte_carlo_simulation(request.human_confidence, request.risk_tolerance, n_runs)
    
    # Métricas
    cvar_95 = quantify_cvar(results)
    omega_score = compute_omega_score(request.human_confidence, request.risk_tolerance, results)
    recommendation = recommend_action(omega_score, cvar_95)
    probability_success = float(np.mean(results > 0.5))
    
    return CalibrationResponse(
        omega_score=round(omega_score, 4),
        cvar_95=round(cvar_95, 4),
        recommendation=recommendation,
        monte_carlo_runs=n_runs,
        probability_success=round(probability_success, 4)
    )

@app.get("/health")
async def health():
    return {"status": "ok", "service": "SymbiOS-AI-Core"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
