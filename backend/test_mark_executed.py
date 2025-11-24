#!/usr/bin/env python3
"""
Test script for mark_executed implementation
"""
import sys
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from blockchain.pose_client import PoSEClient, ActionType, ProposalStatus

def test_mark_executed():
    """Test the mark_executed functionality"""
    print("=" * 80)
    print("🧪 TESTING mark_executed IMPLEMENTATION")
    print("=" * 80)

    # Create client in mock mode with reduced total_staked for easier quorum
    client = PoSEClient(mock_mode=True, voting_period=2)
    client.mock_total_staked = 1000  # Reduce to 1K tokens for easier testing

    # Step 1: Create a proposal
    print("\n📝 Step 1: Creating proposal...")
    proposal_id = client.propose(
        action_type=ActionType.SCALE_UP,
        action_data={'replicas': 5, 'reason': 'High CPU usage'},
        omega_score=0.92,
        psi_index=0.95,
        beta_antifragile=1.15
    )
    print(f"   ✅ Proposal created: ID={proposal_id}")

    # Step 2: Vote and approve
    print(f"\n🗳️  Step 2: Voting on proposal...")
    client.vote(proposal_id, support=True)
    # Add more votes to reach quorum
    for i in range(10):
        client._mock_vote(proposal_id, support=True)

    # Step 3: Finalize to approve
    print(f"\n⏰ Step 3: Finalizing proposal...")
    client.finalize(proposal_id)
    proposal = client.get_proposal(proposal_id)
    print(f"   Status after finalize: {proposal.status.name}")
    assert proposal.status == ProposalStatus.APPROVED, "Proposal should be approved"

    # Step 4: Mark as executed (this is what we implemented!)
    print(f"\n✨ Step 4: Marking proposal as EXECUTED (NEW IMPLEMENTATION)...")
    marked = client.mark_executed(proposal_id)
    print(f"   mark_executed returned: {marked}")

    # Step 5: Verify it's now EXECUTED
    proposal = client.get_proposal(proposal_id)
    print(f"   Final status: {proposal.status.name}")

    if proposal.status == ProposalStatus.EXECUTED:
        print("\n" + "=" * 80)
        print("✅ SUCCESS! mark_executed works correctly!")
        print("=" * 80)
        return True
    else:
        print("\n" + "=" * 80)
        print("❌ FAILED! Proposal status is not EXECUTED")
        print("=" * 80)
        return False

def test_mark_executed_not_approved():
    """Test that mark_executed fails if proposal not approved"""
    print("\n" + "=" * 80)
    print("🧪 TESTING mark_executed WITH REJECTED PROPOSAL")
    print("=" * 80)

    client = PoSEClient(mock_mode=True, voting_period=2)
    client.mock_total_staked = 1000  # Reduce to 1K tokens for easier testing

    # Create and reject proposal
    print("\n📝 Creating and rejecting proposal...")
    proposal_id = client.propose(
        action_type=ActionType.SCALE_DOWN,
        action_data={'replicas': 2},
        omega_score=0.65,
        psi_index=0.70,
        beta_antifragile=0.95
    )

    # Vote against
    for i in range(10):
        client._mock_vote(proposal_id, support=False)

    client.finalize(proposal_id)
    proposal = client.get_proposal(proposal_id)
    print(f"   Status: {proposal.status.name}")

    # Try to mark as executed (should fail)
    print(f"\n🚫 Trying to mark REJECTED proposal as executed...")
    marked = client.mark_executed(proposal_id)
    print(f"   mark_executed returned: {marked}")

    if not marked:
        print("\n✅ Correctly refused to mark rejected proposal as executed!")
        return True
    else:
        print("\n❌ FAILED! Should not allow marking rejected proposal as executed")
        return False

if __name__ == "__main__":
    test1 = test_mark_executed()
    test2 = test_mark_executed_not_approved()

    print("\n" + "=" * 80)
    if test1 and test2:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
