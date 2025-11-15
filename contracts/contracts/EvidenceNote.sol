// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title EvidenceNote
 * @dev ERC-721 NFT para "Evidence Notes" — Prova imutável de decisões no blockchain
 * Cada decisão calibrada gera 1 NFT com Ω-Score, CVaR e prova on-chain
 */
contract EvidenceNote is ERC721, Ownable {
    
    struct Evidence {
        string decision_title;
        uint256 omega_score_scaled;  // 9584 = 0.9584
        uint256 cvar_95_scaled;      // 185 = 0.0185
        bytes32 context_hash;        // SHA256(contexto)
        uint256 timestamp;
        address decision_maker;
    }
    
    mapping(uint256 => Evidence) public evidences;
    uint256 public token_counter;
    
    event EvidenceMinted(uint256 indexed tokenId, address indexed to, uint256 omega_score);
    
    constructor() ERC721("SymbiOS-EvidenceNote", "EVIDENCE") {}
    
    /**
     * @dev Mint novo Evidence NFT
     */
    function mint_evidence(
        address to,
        string memory decision_title,
        uint256 omega_score_scaled,
        uint256 cvar_95_scaled,
        bytes32 context_hash
    ) public onlyOwner returns (uint256) {
        uint256 tokenId = token_counter;
        token_counter++;
        
        evidences[tokenId] = Evidence(
            decision_title,
            omega_score_scaled,
            cvar_95_scaled,
            context_hash,
            block.timestamp,
            to
        );
        
        _safeMint(to, tokenId);
        emit EvidenceMinted(tokenId, to, omega_score_scaled);
        
        return tokenId;
    }
    
    /**
     * @dev Retrieve Evidence by token ID
     */
    function get_evidence(uint256 tokenId) public view returns (Evidence memory) {
        require(_exists(tokenId), "Token does not exist");
        return evidences[tokenId];
    }
    
    /**
     * @dev Check if evidence is antifrágil (Ω > 0.85)
     */
    function is_antifragile(uint256 tokenId) public view returns (bool) {
        require(_exists(tokenId), "Token does not exist");
        return evidences[tokenId].omega_score_scaled > 8500; // 0.85
    }
}
