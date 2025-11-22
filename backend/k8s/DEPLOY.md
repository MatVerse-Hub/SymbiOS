# MatVerse Autonomy - Deployment Guide

Guia completo para deploy do sistema de autonomia MatVerse com blockchain governance.

## 📋 Pré-requisitos

- **Kubernetes 1.24+**
- **Helm 3.0+**
- **kubectl** configurado
- **(Opcional) Blockchain node** (Ethereum, Polygon, etc.)

## 🚀 Quick Start

### 1. Install CRD

```bash
kubectl apply -f k8s/crds/matversescaling.yaml
```

Verifique:
```bash
kubectl get crd matversescalings.matverse.io
```

### 2. Deploy Operator via Helm

```bash
helm install matverse-autonomy ./k8s/helm/matverse-autonomy \
  --namespace matverse-system \
  --create-namespace
```

### 3. Create MatVerseScaling Resource

```bash
kubectl apply -f k8s/examples/matversescaling-example.yaml
```

### 4. Verify

```bash
# Check operator
kubectl get pods -n matverse-system

# Check MatVerseScaling
kubectl get mvs -n default

# Check status
kubectl describe mvs my-app-autoscaling -n default
```

## 📦 Deployment Options

### Option A: Helm (Recommended)

**Install with default values:**
```bash
helm install matverse-autonomy ./k8s/helm/matverse-autonomy
```

**Install with blockchain enabled:**
```bash
helm install matverse-autonomy ./k8s/helm/matverse-autonomy \
  --set operator.blockchain.enabled=true \
  --set operator.blockchain.rpcUrl=http://eth-node:8545 \
  --set operator.blockchain.contractAddress=0x1234...
```

**Install with custom values:**
```bash
helm install matverse-autonomy ./k8s/helm/matverse-autonomy \
  -f custom-values.yaml
```

### Option B: Raw Manifests

```bash
# 1. Create namespace
kubectl create namespace matverse-system

# 2. Apply CRD
kubectl apply -f k8s/crds/matversescaling.yaml

# 3. Apply RBAC
kubectl apply -f k8s/deploy/operator-rbac.yaml

# 4. Deploy operator
kubectl apply -f k8s/deploy/operator-deployment.yaml

# 5. Create MatVerseScaling CR
kubectl apply -f k8s/examples/matversescaling-example.yaml
```

## 🎛️ Configuration

### MatVerseScaling CR

```yaml
apiVersion: matverse.io/v1alpha1
kind: MatVerseScaling
metadata:
  name: my-app-autoscaling
  namespace: default
spec:
  # Target deployment
  targetRef:
    name: my-app
    kind: Deployment

  # Scaling limits
  minReplicas: 2
  maxReplicas: 20

  # Decision mode (conservative, balanced, aggressive)
  mode: balanced

  # Blockchain governance
  blockchain:
    enabled: true
    contractAddress: "0x..."
    rpcUrl: "http://localhost:8545"
    requireApproval: true
    votingTimeout: 120

  # MatVerse targets
  targets:
    omegaScore: 0.95
    psiIndex: 0.97
    betaAntifragile: 1.2
    cpuTarget: 0.70
    latencyTarget: 100
```

### Helm Values

```yaml
# values.yaml
operator:
  image:
    repository: matverse/operator
    tag: "1.0.0"

  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi

  blockchain:
    enabled: true
    rpcUrl: "http://eth-node:8545"
    wsUrl: "ws://eth-node:8546"
    contractAddress: "0x1234567890abcdef..."

  logLevel: DEBUG
```

## 🔗 Blockchain Integration

### 1. Deploy Smart Contract

```bash
# Compile contract
cd blockchain/contracts
solc --optimize --bin --abi PoSEVoting.sol -o build/

# Deploy via Hardhat/Truffle/Remix
```

### 2. Configure Operator

```bash
export CONTRACT_ADDRESS="0x..."
export RPC_URL="http://eth-node:8545"

helm upgrade matverse-autonomy ./k8s/helm/matverse-autonomy \
  --set operator.blockchain.contractAddress=$CONTRACT_ADDRESS \
  --set operator.blockchain.rpcUrl=$RPC_URL \
  --reuse-values
```

### 3. Stake Tokens (for voting)

```bash
# Via CLI ou smart contract interface
cast send $CONTRACT_ADDRESS "stake(uint256)" 1000000000000000000 \
  --rpc-url $RPC_URL \
  --private-key $PRIVATE_KEY
```

## 📊 Monitoring

### Metrics

O operator expõe métricas Prometheus:
- `matverse_decisions_total` - Total de decisões
- `matverse_actions_executed` - Ações executadas
- `matverse_proposals_created` - Propostas blockchain
- `matverse_omega_score` - Ω-Score atual
- `matverse_psi_index` - Ψ-Index atual

### Logs

```bash
# Operator logs
kubectl logs -f -n matverse-system deployment/matverse-operator

# Decision logs
kubectl logs -f -n matverse-system deployment/matverse-operator | grep "Decision:"

# Blockchain logs
kubectl logs -f -n matverse-system deployment/matverse-operator | grep "Blockchain:"
```

### Status

```bash
# Get MatVerseScaling status
kubectl get mvs -o wide

# Describe for details
kubectl describe mvs my-app-autoscaling

# Watch status updates
watch kubectl get mvs
```

## 🧪 Testing

### Local Testing (Mock Mode)

```bash
# Testa operator localmente sem K8s
cd backend
python3 autonomy/decision_engine.py

# Testa blockchain integration
python3 autonomy/blockchain_integration.py

# Testa event listener
python3 blockchain/event_listener.py
```

### Integration Testing

```bash
# Deploy em cluster de teste (kind/minikube)
kind create cluster --name matverse-test

# Install operator
helm install matverse-autonomy ./k8s/helm/matverse-autonomy

# Create test deployment
kubectl create deployment test-app --image=nginx --replicas=3

# Create MatVerseScaling
cat <<EOF | kubectl apply -f -
apiVersion: matverse.io/v1alpha1
kind: MatVerseScaling
metadata:
  name: test-autoscaling
spec:
  targetRef:
    name: test-app
  minReplicas: 1
  maxReplicas: 10
  mode: aggressive
  blockchain:
    enabled: false  # Mock mode
EOF

# Monitor
kubectl get mvs test-autoscaling -w
```

## 🛠️ Troubleshooting

### Operator não inicia

```bash
# Check RBAC
kubectl auth can-i list matversescalings.matverse.io --as=system:serviceaccount:matverse-system:matverse-operator

# Check CRD
kubectl get crd matversescalings.matverse.io

# Check logs
kubectl logs -n matverse-system deployment/matverse-operator
```

### MatVerseScaling não atualiza status

```bash
# Verify operator is running
kubectl get pods -n matverse-system

# Check events
kubectl get events --field-selector involvedObject.name=my-app-autoscaling

# Check operator logs
kubectl logs -n matverse-system deployment/matverse-operator | grep my-app-autoscaling
```

### Blockchain connection failed

```bash
# Test RPC connectivity
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  $RPC_URL

# Check contract address
cast code $CONTRACT_ADDRESS --rpc-url $RPC_URL

# Verify operator env vars
kubectl get deployment matverse-operator -n matverse-system -o yaml | grep -A 10 env:
```

## 🔄 Upgrade

```bash
# Upgrade via Helm
helm upgrade matverse-autonomy ./k8s/helm/matverse-autonomy \
  --reuse-values

# Update CRD (se necessário)
kubectl apply -f k8s/crds/matversescaling.yaml

# Restart operator
kubectl rollout restart deployment/matverse-operator -n matverse-system
```

## 🗑️ Uninstall

```bash
# Delete MatVerseScaling resources
kubectl delete mvs --all

# Uninstall via Helm
helm uninstall matverse-autonomy

# Delete CRD (optional - destroys all CRs)
kubectl delete crd matversescalings.matverse.io

# Delete namespace
kubectl delete namespace matverse-system
```

## 📚 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MatVerse Autonomy                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │   Metrics   │───▶│   Decision   │───▶│  Kalman  │  │
│  │  Collector  │    │    Engine    │    │  Policy  │  │
│  └─────────────┘    └──────────────┘    └──────────┘  │
│         │                   │                   │       │
│         ▼                   ▼                   ▼       │
│  ┌─────────────────────────────────────────────────┐  │
│  │         Blockchain Decision Engine              │  │
│  │  (OODA Loop + PoSE Voting)                      │  │
│  └─────────────────────────────────────────────────┘  │
│         │                   │                   │       │
│         ▼                   ▼                   ▼       │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐│
│  │  PoSE    │    │  K8s         │    │  Event       ││
│  │  Client  │    │  Actuator    │    │  Listener    ││
│  └──────────┘    └──────────────┘    └──────────────┘│
│         │                   │                   │       │
└─────────┼───────────────────┼───────────────────┼───────┘
          │                   │                   │
          ▼                   ▼                   ▼
   ┌───────────┐      ┌─────────────┐     ┌──────────┐
   │Blockchain │      │ Kubernetes  │     │ WebSocket│
   │   Node    │      │   Cluster   │     │  Events  │
   └───────────┘      └─────────────┘     └──────────┘
```

## 🎓 Next Steps

1. **Monitor Performance**: Acompanhe métricas de Ω-Score, Ψ-Index, β
2. **Tune Decision Mode**: Ajuste `conservative`, `balanced`, `aggressive`
3. **Scale Testing**: Teste sob carga com ferramentas como k6, Locust
4. **Blockchain Governance**: Participe de votações via staking
5. **Contribute**: Melhore o código no [GitHub](https://github.com/MatVerse-Hub/SymbiOS)

## 📞 Support

- **Documentation**: https://docs.matverse.io
- **Issues**: https://github.com/MatVerse-Hub/SymbiOS/issues
- **Community**: https://discord.gg/matverse

---

**MatVerse Team** | [matverse.io](https://matverse.io)
