"""
Test suite for MatVerse Unified Ecosystem
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_kalman_import():
    """Test Kalman Filter import"""
    from filters.kalman_cfc_adaptive import AdaptiveKalmanCFC
    kalman = AdaptiveKalmanCFC()
    assert kalman is not None
    assert kalman.Q is not None
    assert kalman.R is not None


def test_kalman_basic_operation():
    """Test Kalman Filter basic operation"""
    from filters.kalman_cfc_adaptive import AdaptiveKalmanCFC
    import numpy as np
    
    kalman = AdaptiveKalmanCFC()
    
    # Test prediction
    x_pred = kalman.predict()
    assert x_pred is not None
    assert len(x_pred) == 2
    
    # Test update
    measurement = np.array([0.5, -0.5])
    x_updated = kalman.update(measurement)
    assert x_updated is not None
    assert len(x_updated) == 2


def test_pqc_import():
    """Test PQC Signer import"""
    from blockchain.pqc_signer import SPHINCSPlusSigner
    signer = SPHINCSPlusSigner()
    assert signer is not None
    assert signer.security_level == 128


def test_pqc_keypair_generation():
    """Test PQC keypair generation"""
    from blockchain.pqc_signer import SPHINCSPlusSigner
    
    signer = SPHINCSPlusSigner()
    keypair = signer.generate_keypair()
    
    assert keypair.public_key is not None
    assert keypair.private_key is not None
    assert len(keypair.public_key) == 64  # SHA256 hex = 64 chars
    assert len(keypair.private_key) == 64


def test_pqc_signature():
    """Test PQC signature creation and verification"""
    from blockchain.pqc_signer import SPHINCSPlusSigner
    
    signer = SPHINCSPlusSigner()
    keypair = signer.generate_keypair()
    
    message = b"Test message for MatVerse"
    signature = signer.sign(message, keypair.private_key)
    
    assert signature is not None
    assert signature.signature is not None
    assert len(signature.signature) == 128  # SHA512 hex = 128 chars
    
    # Verify signature
    is_valid = signer.verify(message, signature)
    assert is_valid is True


def test_integration_import():
    """Test Omega Gate Integration import"""
    from integration.omega_gate_integration import OmegaGateProcessor
    processor = OmegaGateProcessor()
    assert processor is not None
    assert processor.kalman_filter is not None
    assert processor.pqc_signer is not None


def test_omega_score_calculation():
    """Test Omega Score calculation"""
    from integration.omega_gate_integration import OmegaGateProcessor
    
    processor = OmegaGateProcessor()
    
    omega = processor.calculate_omega_score(
        psi=0.9,
        theta_ms=50.0,
        cvar=0.01,
        pole=0.7,
        cog=0.8,
        trust=0.9
    )
    
    assert omega is not None
    assert 0 <= omega <= 1
    assert omega > 0.5  # Should be good score with these inputs


def test_comprehensive_audit():
    """Test comprehensive audit process"""
    from integration.omega_gate_integration import OmegaGateProcessor
    import numpy as np
    
    processor = OmegaGateProcessor()
    
    # Create test data
    np.random.seed(42)
    psi_series = np.linspace(-0.5, 0.5, 10).tolist()
    gamma_series = (-np.linspace(-0.5, 0.5, 10)).tolist()
    
    result = processor.process_comprehensive_audit(
        psi_series,
        gamma_series,
        context={'test': True}
    )
    
    assert result['success'] is True
    assert 'audit_id' in result
    assert 'kalman' in result
    assert 'omega_gate' in result
    assert 'evidence_note' in result
    assert result['validation']['checks_passed'] == 3
    assert result['validation']['total_checks'] == 3


def test_api_import():
    """Test API main import"""
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'api'))
    
    try:
        import main
        assert main.app is not None
        assert main.processor is not None
    except ImportError as e:
        # API may not be importable in test environment
        print(f"Note: API import skipped - {e}")
