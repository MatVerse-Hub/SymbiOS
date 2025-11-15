// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title OmegaGate
 * @dev Validação de risco semântico (CVaR-POVM)
 * Filtra decisões com risco alto ou baixa antifragilidade
 */
contract OmegaGate {
    
    uint256 public constant OMEGA_THRESHOLD = 8500; // 0.85
    uint256 public constant CVAR_MAX = 500;         // 0.05
    
    enum Decision { ACCELERATE, MONITOR, PAUSE }
    
    event DecisionEvaluated(address indexed user, Decision recommendation, uint256 omega_score);
    
    /**
     * @dev Avalia decisão e recomenda ação
     */
    function evaluate(
        uint256 omega_score_scaled,
        uint256 cvar_95_scaled
    ) public returns (Decision) {
        Decision recommendation;
        
        if (omega_score_scaled >= OMEGA_THRESHOLD && cvar_95_scaled < CVAR_MAX) {
            recommendation = Decision.ACCELERATE;
        } else if (omega_score_scaled >= 7000) {
            recommendation = Decision.MONITOR;
        } else {
            recommendation = Decision.PAUSE;
        }
        
        emit DecisionEvaluated(msg.sender, recommendation, omega_score_scaled);
        return recommendation;
    }
}
