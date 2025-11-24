# BASE44_COMPONENTS.md - Integração Base44 no symbiOS

**Status**: 🚧 Planejado (Dezembro 2025)
**Última atualização**: 23 de novembro de 2025
**Versão**: 1.0

---

## 📋 Visão Geral

Este documento descreve a integração do **Base44** no symbiOS, incluindo componentes React, configuração de API, e estratégias de sincronização de dados em tempo real.

**Base44** é uma plataforma de gerenciamento de entidades e eventos que será usada no symbiOS para:
- Rastreamento de Evidence Notes em tempo real
- Dashboard de métricas Ω-GATE
- Sincronização de estados entre múltiplos nós
- Filtros e análises de dados quânticos

---

## 🔑 Configuração Base44

### Credenciais (Desenvolvimento)

```typescript
// frontend/src/config/base44.config.ts

export const BASE44_CONFIG = {
  API_KEY: "431d90fd5dc046bea66c70686ed2a343",
  APP_ID: "69224f836e8f58657363c48f",
  ENTITY: "symbiOS",
  BASE_URL: "https://app.base44.com/api/apps",
  VERSION: "v1"
};

// Para produção, mover para variáveis de ambiente:
// VITE_BASE44_API_KEY=...
// VITE_BASE44_APP_ID=...
```

### Estrutura de Entidade Principal

```typescript
interface SimbiOSEntity {
  id: string;
  name: "symbiOS";
  type: "quantum_os";
  metadata: {
    omega_score: number;
    cfc_score: number;
    evidence_notes_count: number;
    last_audit_timestamp: number;
    antifragile_beta: number;
  };
  status: "operational" | "degraded" | "offline";
  created_at: string;
  updated_at: string;
}
```

---

## 🧩 Componentes React (Planejados)

### 1. Base44EntityManager

**Arquivo**: `frontend/src/components/matverse/Base44EntityManager.tsx`

**Propósito**: Gerenciar entidades Base44 (criar, atualizar, deletar)

**Interface**:
```typescript
interface Base44EntityManagerProps {
  entityType: "evidence_note" | "audit_result" | "quantum_state";
  onEntityCreated?: (entity: any) => void;
  onEntityUpdated?: (entity: any) => void;
  onEntityDeleted?: (entityId: string) => void;
}

export const Base44EntityManager: React.FC<Base44EntityManagerProps> = ({
  entityType,
  onEntityCreated,
  onEntityUpdated,
  onEntityDeleted
}) => {
  // Implementação usando shadcn/ui + lucide-react
  // - Form para criar/editar entidades
  // - Table para listar entidades
  // - Dialog para confirmação de deleção
  // - Toast para feedback de ações

  return (
    <Card className="dark:bg-slate-900">
      <CardHeader>
        <CardTitle>Entity Manager - {entityType}</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Form + Table + Actions */}
      </CardContent>
    </Card>
  );
};
```

**Funcionalidades**:
- ✅ CRUD completo de entidades
- ✅ Validação com Zod
- ✅ Loading states com Skeleton
- ✅ Error handling com Toast
- ✅ Pagination para listas grandes

---

### 2. Base44LiveSync

**Arquivo**: `frontend/src/components/matverse/Base44LiveSync.tsx`

**Propósito**: Sincronização em tempo real via WebSocket/SSE

**Interface**:
```typescript
interface Base44LiveSyncProps {
  entityId: string;
  onUpdate: (data: any) => void;
  syncInterval?: number; // ms (padrão: 1000 para 50Hz se suportado)
}

export const Base44LiveSync: React.FC<Base44LiveSyncProps> = ({
  entityId,
  onUpdate,
  syncInterval = 1000
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    // Conecta WebSocket ou polling
    const ws = new WebSocket(`${BASE44_CONFIG.WS_URL}/${entityId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onUpdate(data);
      setLastUpdate(new Date());
    };

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);

    return () => ws.close();
  }, [entityId]);

  return (
    <div className="flex items-center gap-2">
      <Badge variant={isConnected ? "success" : "destructive"}>
        {isConnected ? "🟢 Live" : "🔴 Offline"}
      </Badge>
      {lastUpdate && (
        <span className="text-sm text-muted-foreground">
          Last update: {lastUpdate.toLocaleTimeString()}
        </span>
      )}
    </div>
  );
};
```

**Funcionalidades**:
- ✅ WebSocket connection com auto-reconnect
- ✅ Fallback para polling se WS falhar
- ✅ Indicador visual de conexão
- ✅ Timestamp de última atualização
- ✅ Buffer para evitar re-renders excessivos

---

### 3. Base44FilterableDashboard

**Arquivo**: `frontend/src/components/matverse/Base44FilterableDashboard.tsx`

**Propósito**: Dashboard com filtros avançados para análise de dados

**Interface**:
```typescript
interface Base44FilterableDashboardProps {
  dataSource: "evidence_notes" | "audits" | "quantum_states";
  initialFilters?: DashboardFilters;
}

interface DashboardFilters {
  dateRange?: { start: Date; end: Date };
  omegaScoreMin?: number;
  cfcScoreMin?: number;
  status?: ("approved" | "rejected" | "pending")[];
  tags?: string[];
}

export const Base44FilterableDashboard: React.FC<Base44FilterableDashboardProps> = ({
  dataSource,
  initialFilters
}) => {
  const [filters, setFilters] = useState<DashboardFilters>(initialFilters || {});
  const [data, setData] = useState([]);

  // Fetch data com filtros
  useEffect(() => {
    fetchFilteredData(dataSource, filters).then(setData);
  }, [dataSource, filters]);

  return (
    <div className="space-y-4">
      {/* Filter Bar */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-4">
          <DateRangePicker onChange={(range) => setFilters({...filters, dateRange: range})} />
          <Slider
            label="Min Ω-Score"
            min={0}
            max={1}
            step={0.01}
            value={filters.omegaScoreMin || 0}
            onChange={(val) => setFilters({...filters, omegaScoreMin: val})}
          />
          <MultiSelect
            label="Status"
            options={["approved", "rejected", "pending"]}
            value={filters.status || []}
            onChange={(val) => setFilters({...filters, status: val})}
          />
        </CardContent>
      </Card>

      {/* Data Grid */}
      <Card>
        <CardHeader>
          <CardTitle>Results ({data.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={data} />
        </CardContent>
      </Card>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Ω-Score Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={aggregateByOmegaScore(data)}>
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={aggregateByTime(data)}>
                <Line type="monotone" dataKey="omega_score" stroke="#82ca9d" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
```

**Funcionalidades**:
- ✅ Filtros múltiplos (data, scores, status, tags)
- ✅ Data grid com sorting e pagination
- ✅ Gráficos interativos (recharts)
- ✅ Export para CSV/JSON
- ✅ Salvamento de presets de filtros

---

### 4. Base44StatusTracker

**Arquivo**: `frontend/src/components/matverse/Base44StatusTracker.tsx`

**Propósito**: Rastreamento de status do sistema em tempo real

**Interface**:
```typescript
interface Base44StatusTrackerProps {
  systemId: string;
  refreshInterval?: number; // ms
}

export const Base44StatusTracker: React.FC<Base44StatusTrackerProps> = ({
  systemId,
  refreshInterval = 5000
}) => {
  const [status, setStatus] = useState<SystemStatus | null>(null);

  useInterval(() => {
    fetchSystemStatus(systemId).then(setStatus);
  }, refreshInterval);

  if (!status) return <Skeleton className="h-32" />;

  return (
    <Card className="dark:bg-slate-900">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>System Status</span>
          <Badge variant={getStatusVariant(status.health)}>
            {status.health.toUpperCase()}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Métricas principais */}
        <div className="grid grid-cols-2 gap-4">
          <MetricCard
            label="Ω-Score"
            value={status.omega_score.toFixed(3)}
            trend={status.omega_trend}
            icon={<Target />}
          />
          <MetricCard
            label="CFC Score"
            value={status.cfc_score.toFixed(3)}
            trend={status.cfc_trend}
            icon={<Zap />}
          />
          <MetricCard
            label="Latency"
            value={`${status.latency_ms.toFixed(2)}ms`}
            trend={status.latency_trend}
            icon={<Clock />}
          />
          <MetricCard
            label="Evidence Notes"
            value={status.evidence_notes_count}
            trend={status.evidence_trend}
            icon={<FileText />}
          />
        </div>

        {/* Timeline de eventos */}
        <Separator />
        <div>
          <h4 className="text-sm font-semibold mb-2">Recent Events</h4>
          <ScrollArea className="h-32">
            {status.recent_events.map((event, i) => (
              <div key={i} className="flex items-start gap-2 py-2">
                <Badge variant="outline">{event.type}</Badge>
                <span className="text-sm">{event.message}</span>
                <span className="text-xs text-muted-foreground ml-auto">
                  {formatDistanceToNow(new Date(event.timestamp))}
                </span>
              </div>
            ))}
          </ScrollArea>
        </div>

        {/* Alertas ativos */}
        {status.active_alerts.length > 0 && (
          <>
            <Separator />
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Active Alerts ({status.active_alerts.length})</AlertTitle>
              <AlertDescription>
                <ul className="list-disc pl-4">
                  {status.active_alerts.map((alert, i) => (
                    <li key={i}>{alert.message}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          </>
        )}
      </CardContent>
    </Card>
  );
};
```

**Funcionalidades**:
- ✅ Métricas em tempo real
- ✅ Timeline de eventos
- ✅ Alertas ativos
- ✅ Trends (↑↓) visuais
- ✅ Auto-refresh configurável

---

## 🔌 API Client

### Hook Customizado para Base44

**Arquivo**: `frontend/src/hooks/useBase44.ts`

```typescript
import { useState, useEffect } from 'react';
import { BASE44_CONFIG } from '@/config/base44.config';

interface UseBase44Options {
  entityType?: string;
  autoFetch?: boolean;
  refreshInterval?: number;
}

export const useBase44 = (options: UseBase44Options = {}) => {
  const { entityType, autoFetch = false, refreshInterval } = options;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchEntity = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${BASE44_CONFIG.BASE_URL}/${BASE44_CONFIG.APP_ID}/entities/${id}`,
        {
          headers: {
            'Authorization': `Bearer ${BASE44_CONFIG.API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setData(data);
      return data;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const createEntity = async (payload: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${BASE44_CONFIG.BASE_URL}/${BASE44_CONFIG.APP_ID}/entities`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${BASE44_CONFIG.API_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        }
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setData(data);
      return data;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateEntity = async (id: string, payload: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${BASE44_CONFIG.BASE_URL}/${BASE44_CONFIG.APP_ID}/entities/${id}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${BASE44_CONFIG.API_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        }
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setData(data);
      return data;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteEntity = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${BASE44_CONFIG.BASE_URL}/${BASE44_CONFIG.APP_ID}/entities/${id}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${BASE44_CONFIG.API_KEY}`
          }
        }
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setData(null);
      return true;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Auto-fetch on mount
  useEffect(() => {
    if (autoFetch && entityType) {
      fetchEntity(entityType);
    }
  }, [autoFetch, entityType]);

  // Auto-refresh
  useEffect(() => {
    if (refreshInterval && entityType) {
      const interval = setInterval(() => {
        fetchEntity(entityType);
      }, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval, entityType]);

  return {
    data,
    loading,
    error,
    fetchEntity,
    createEntity,
    updateEntity,
    deleteEntity
  };
};
```

---

## 📊 Integração com Backend symbiOS

### Sincronização Evidence Notes → Base44

**Arquivo**: `backend/src/integration/base44_sync.py`

```python
import aiohttp
from typing import Dict, Any
from datetime import datetime

BASE44_CONFIG = {
    "api_key": "431d90fd5dc046bea66c70686ed2a343",
    "app_id": "69224f836e8f58657363c48f",
    "base_url": "https://app.base44.com/api/apps"
}

class Base44Syncer:
    def __init__(self):
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {BASE44_CONFIG['api_key']}",
                "Content-Type": "application/json"
            }
        )
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def sync_evidence_note(
        self,
        evidence_id: str,
        omega_score: float,
        cfc_score: float,
        pqc_signature: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sincroniza Evidence Note com Base44"""
        payload = {
            "type": "evidence_note",
            "external_id": evidence_id,
            "data": {
                "omega_score": omega_score,
                "cfc_score": cfc_score,
                "pqc_signature": pqc_signature,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata
            },
            "tags": [
                f"omega:{int(omega_score * 100)}",
                f"cfc:{int(cfc_score * 100)}",
                "symbios",
                "pqc"
            ]
        }

        url = f"{BASE44_CONFIG['base_url']}/{BASE44_CONFIG['app_id']}/entities"

        async with self.session.post(url, json=payload) as response:
            if response.status != 201:
                raise Exception(f"Base44 sync failed: {response.status}")
            return await response.json()

    async def query_evidence_notes(
        self,
        omega_min: float = 0.0,
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """Query Evidence Notes do Base44"""
        url = f"{BASE44_CONFIG['base_url']}/{BASE44_CONFIG['app_id']}/entities"
        params = {
            "type": "evidence_note",
            "tags": f"omega>={int(omega_min * 100)}",
            "limit": limit
        }

        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"Base44 query failed: {response.status}")
            return await response.json()
```

### Uso no API Endpoint

```python
# backend/src/api/main.py

from integration.base44_sync import Base44Syncer

@app.post("/unified/audit/comprehensive")
async def comprehensive_audit(request: AuditRequest):
    # ... processamento existente ...

    # Sincroniza com Base44
    async with Base44Syncer() as syncer:
        await syncer.sync_evidence_note(
            evidence_id=result['audit_id'],
            omega_score=result['omega_gate']['omega_score'],
            cfc_score=result['kalman']['cfc_score'],
            pqc_signature=result['evidence_note']['pqc_signature'],
            metadata={
                "fidelity": result['kalman']['fidelity_new'],
                "coherence": result['kalman']['coherence'],
                "latency_ms": result['kalman']['processing_time_ms']
            }
        )

    return result
```

---

## 🎯 Roadmap de Implementação

### Fase 1: Setup (Semana 1)
- [ ] Criar estrutura de pastas `frontend/src/components/matverse/`
- [ ] Configurar Base44 config
- [ ] Criar hook `useBase44`
- [ ] Setup shadcn/ui components

### Fase 2: Componentes Básicos (Semana 2)
- [ ] Implementar `Base44EntityManager`
- [ ] Implementar `Base44StatusTracker`
- [ ] Testes unitários com Vitest

### Fase 3: Componentes Avançados (Semana 3)
- [ ] Implementar `Base44LiveSync`
- [ ] Implementar `Base44FilterableDashboard`
- [ ] Integração com backend Python

### Fase 4: Polimento (Semana 4)
- [ ] Testes E2E com Playwright
- [ ] Performance optimization
- [ ] Documentação de uso
- [ ] Deploy em staging

---

## 🔒 Segurança

### Proteção de API Keys

```typescript
// ❌ NUNCA fazer isso em produção:
const API_KEY = "431d90fd5dc046bea66c70686ed2a343";

// ✅ SEMPRE usar variáveis de ambiente:
const API_KEY = import.meta.env.VITE_BASE44_API_KEY;

// ✅ MELHOR: Proxy via backend
// Frontend chama /api/base44/entities
// Backend adiciona API_KEY nos headers
```

### Rate Limiting

```python
# backend/src/api/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/base44/entities")
@limiter.limit("10/minute")
async def proxy_base44_create(request: Request):
    # Proxy para Base44 com API_KEY segura no backend
    pass
```

---

## 📖 Referências

- **Base44 Docs**: https://docs.base44.com (assumido)
- **shadcn/ui**: https://ui.shadcn.com
- **Recharts**: https://recharts.org
- **React Query**: https://tanstack.com/query (para caching)

---

**Status**: 🚧 **Documentação completa - Aguardando implementação**

**Próximo passo**: Criar estrutura de pastas e implementar `useBase44` hook.
