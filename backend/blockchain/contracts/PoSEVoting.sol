// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title PoSE Voting Contract
 * @notice Proof of Symbiotic Evolution - Autonomous Decision Voting
 * @dev Implements on-chain voting for MatVerse autonomous decisions
 *
 * Author: MatVerse Team
 * Version: 1.0.0
 * Date: 2025-11-22
 */

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract PoSEVoting is Ownable, ReentrancyGuard {

    // ========== STRUCTS ==========

    /// @notice Proposed autonomous action
    struct Proposal {
        uint256 id;
        address proposer;
        ActionType actionType;
        bytes actionData;

        uint256 votesFor;
        uint256 votesAgainst;

        uint256 createdAt;
        uint256 deadline;

        ProposalStatus status;

        // MatVerse metrics at proposal time
        uint256 omegaScore;      // Ω-Score * 1000 (0.95 -> 950)
        uint256 psiIndex;        // Ψ-Index * 1000
        uint256 betaAntifragile; // β * 1000
    }

    /// @notice Type of autonomous action
    enum ActionType {
        SCALE_UP,
        SCALE_DOWN,
        RETUNE,
        ROLLBACK,
        EMERGENCY_STOP
    }

    /// @notice Status of proposal
    enum ProposalStatus {
        Pending,
        Approved,
        Rejected,
        Executed,
        Expired
    }

    /// @notice Vote record
    struct Vote {
        address voter;
        uint256 weight;
        bool support;
        uint256 timestamp;
    }

    // ========== STATE VARIABLES ==========

    /// @notice Governance token (staking for voting power)
    IERC20 public governanceToken;

    /// @notice All proposals
    mapping(uint256 => Proposal) public proposals;

    /// @notice Votes per proposal
    mapping(uint256 => mapping(address => Vote)) public votes;

    /// @notice Has address voted on proposal
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    /// @notice Proposal counter
    uint256 public proposalCount;

    /// @notice Minimum stake to propose (in governance tokens)
    uint256 public minStakeToPropose;

    /// @notice Quorum percentage (67% = 6700)
    uint256 public quorumPercentage;

    /// @notice Voting period (in seconds)
    uint256 public votingPeriod;

    /// @notice Total staked governance tokens
    uint256 public totalStaked;

    /// @notice Stake balances
    mapping(address => uint256) public stakes;

    // ========== EVENTS ==========

    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        ActionType actionType,
        uint256 omegaScore,
        uint256 deadline
    );

    event VoteCast(
        uint256 indexed proposalId,
        address indexed voter,
        bool support,
        uint256 weight
    );

    event ProposalApproved(
        uint256 indexed proposalId,
        uint256 votesFor,
        uint256 votesAgainst
    );

    event ProposalRejected(
        uint256 indexed proposalId,
        uint256 votesFor,
        uint256 votesAgainst
    );

    event ProposalExecuted(
        uint256 indexed proposalId,
        address indexed executor
    );

    event Staked(address indexed staker, uint256 amount);
    event Unstaked(address indexed staker, uint256 amount);

    // ========== CONSTRUCTOR ==========

    constructor(
        address _governanceToken,
        uint256 _minStakeToPropose,
        uint256 _quorumPercentage,
        uint256 _votingPeriod
    ) Ownable(msg.sender) {
        require(_governanceToken != address(0), "Invalid token");
        require(_quorumPercentage <= 10000, "Invalid quorum");

        governanceToken = IERC20(_governanceToken);
        minStakeToPropose = _minStakeToPropose;
        quorumPercentage = _quorumPercentage;  // 6700 = 67%
        votingPeriod = _votingPeriod;          // 120 seconds for fast decisions
    }

    // ========== STAKING FUNCTIONS ==========

    /**
     * @notice Stake governance tokens to gain voting power
     * @param amount Amount of tokens to stake
     */
    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Amount must be > 0");

        bool success = governanceToken.transferFrom(msg.sender, address(this), amount);
        require(success, "Transfer failed");

        stakes[msg.sender] += amount;
        totalStaked += amount;

        emit Staked(msg.sender, amount);
    }

    /**
     * @notice Unstake governance tokens
     * @param amount Amount of tokens to unstake
     */
    function unstake(uint256 amount) external nonReentrant {
        require(amount > 0, "Amount must be > 0");
        require(stakes[msg.sender] >= amount, "Insufficient stake");

        stakes[msg.sender] -= amount;
        totalStaked -= amount;

        bool success = governanceToken.transfer(msg.sender, amount);
        require(success, "Transfer failed");

        emit Unstaked(msg.sender, amount);
    }

    // ========== PROPOSAL FUNCTIONS ==========

    /**
     * @notice Create new autonomous action proposal
     * @param actionType Type of action (SCALE_UP, SCALE_DOWN, etc)
     * @param actionData Encoded action parameters
     * @param omegaScore Current Ω-Score * 1000
     * @param psiIndex Current Ψ-Index * 1000
     * @param betaAntifragile Current β * 1000
     */
    function propose(
        ActionType actionType,
        bytes calldata actionData,
        uint256 omegaScore,
        uint256 psiIndex,
        uint256 betaAntifragile
    ) external returns (uint256) {
        require(stakes[msg.sender] >= minStakeToPropose, "Insufficient stake");
        require(omegaScore <= 1000, "Invalid omega score");

        uint256 proposalId = ++proposalCount;
        uint256 deadline = block.timestamp + votingPeriod;

        proposals[proposalId] = Proposal({
            id: proposalId,
            proposer: msg.sender,
            actionType: actionType,
            actionData: actionData,
            votesFor: 0,
            votesAgainst: 0,
            createdAt: block.timestamp,
            deadline: deadline,
            status: ProposalStatus.Pending,
            omegaScore: omegaScore,
            psiIndex: psiIndex,
            betaAntifragile: betaAntifragile
        });

        emit ProposalCreated(
            proposalId,
            msg.sender,
            actionType,
            omegaScore,
            deadline
        );

        return proposalId;
    }

    /**
     * @notice Vote on a proposal
     * @param proposalId ID of proposal
     * @param support True to support, false to oppose
     */
    function vote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];

        require(proposal.id != 0, "Proposal not found");
        require(proposal.status == ProposalStatus.Pending, "Not pending");
        require(block.timestamp < proposal.deadline, "Voting ended");
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        require(stakes[msg.sender] > 0, "No voting power");

        uint256 weight = stakes[msg.sender];

        votes[proposalId][msg.sender] = Vote({
            voter: msg.sender,
            weight: weight,
            support: support,
            timestamp: block.timestamp
        });

        hasVoted[proposalId][msg.sender] = true;

        if (support) {
            proposal.votesFor += weight;
        } else {
            proposal.votesAgainst += weight;
        }

        emit VoteCast(proposalId, msg.sender, support, weight);
    }

    /**
     * @notice Finalize proposal after voting period
     * @param proposalId ID of proposal
     */
    function finalize(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];

        require(proposal.id != 0, "Proposal not found");
        require(proposal.status == ProposalStatus.Pending, "Not pending");
        require(block.timestamp >= proposal.deadline, "Voting not ended");

        uint256 totalVotes = proposal.votesFor + proposal.votesAgainst;
        uint256 requiredQuorum = (totalStaked * quorumPercentage) / 10000;

        // Check quorum
        if (totalVotes < requiredQuorum) {
            proposal.status = ProposalStatus.Expired;
            return;
        }

        // Check majority
        if (proposal.votesFor > proposal.votesAgainst) {
            proposal.status = ProposalStatus.Approved;
            emit ProposalApproved(proposalId, proposal.votesFor, proposal.votesAgainst);
        } else {
            proposal.status = ProposalStatus.Rejected;
            emit ProposalRejected(proposalId, proposal.votesFor, proposal.votesAgainst);
        }
    }

    /**
     * @notice Mark proposal as executed (called by K8s operator)
     * @param proposalId ID of proposal
     */
    function markExecuted(uint256 proposalId) external onlyOwner {
        Proposal storage proposal = proposals[proposalId];

        require(proposal.id != 0, "Proposal not found");
        require(proposal.status == ProposalStatus.Approved, "Not approved");

        proposal.status = ProposalStatus.Executed;

        emit ProposalExecuted(proposalId, msg.sender);
    }

    // ========== VIEW FUNCTIONS ==========

    /**
     * @notice Get proposal details
     * @param proposalId ID of proposal
     */
    function getProposal(uint256 proposalId) external view returns (Proposal memory) {
        return proposals[proposalId];
    }

    /**
     * @notice Check if proposal is approved
     * @param proposalId ID of proposal
     */
    function isApproved(uint256 proposalId) external view returns (bool) {
        return proposals[proposalId].status == ProposalStatus.Approved;
    }

    /**
     * @notice Get voting power of address
     * @param voter Address to check
     */
    function getVotingPower(address voter) external view returns (uint256) {
        return stakes[voter];
    }

    /**
     * @notice Get current quorum threshold
     */
    function getQuorumThreshold() external view returns (uint256) {
        return (totalStaked * quorumPercentage) / 10000;
    }

    // ========== ADMIN FUNCTIONS ==========

    /**
     * @notice Update voting parameters
     */
    function updateParameters(
        uint256 _minStakeToPropose,
        uint256 _quorumPercentage,
        uint256 _votingPeriod
    ) external onlyOwner {
        require(_quorumPercentage <= 10000, "Invalid quorum");

        minStakeToPropose = _minStakeToPropose;
        quorumPercentage = _quorumPercentage;
        votingPeriod = _votingPeriod;
    }
}
