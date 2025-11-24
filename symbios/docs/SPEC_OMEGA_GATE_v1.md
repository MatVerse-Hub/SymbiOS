# Ω-GATE Specification (v1)

Omega Gate scores each inference request with a composite Ψ (psi) score to decide whether the output is approved.

## Inputs
- `model`: identifier of the model used
- `input`: prompt or structured request
- `output`: model output payload (expects `text` key)
- `context`: metadata such as `expected_format`

## Subscores
- **format**: checks if the response is valid JSON
- **policy**: basic keyword filtering against unsafe terms
- **consistency**: structural sanity checks (balanced braces/brackets, limited formatting penalties)
- **coverage**: verifies output references input keys and, when provided, expected format hints

Each subscore is weighted equally (0.25), and Ψ is the weighted sum. Threshold τ (TAU) defaults to `0.85`.

## Decision
- Approved when `psi >= τ`
- Response payload: `{ approved, psi, threshold, subscores }`

## Persistence
When approved, PoSE-Lite captures the request, response, and Ω-GATE decision as evidence.
