# 2.3.2 Graph DFS·BFS·Union-Find·Topological Sort

코딩 인터뷰에서 그래프 문제는 트리보다 한 단계 위의 일반화이며, 사이클이 있을 수 있고 시작점이 여러 개일 수 있다는 점에서 디테일이 늘어납니다. 그러나 풀이의 도구는 결국 DFS, BFS, Union-Find, 위상 정렬의 네 가지로 좁혀집니다. 이 단원에서는 그래프 표현부터 시작해 네 도구를 차례로 정리하고, 어떤 문제에 어느 도구가 맞물리는지를 본 다음 함정을 짚습니다.

먼저 그래프 표현 두 가지를 풀어 두겠습니다. **인접 리스트**는 각 정점에 대해 그 정점과 이어진 이웃들의 리스트를 들고 다니는 형태로, dict[int, list[int]]가 표준입니다. 정점 수가 V, 간선 수가 E일 때 공간은 O(V + E)이고, 한 정점의 이웃을 모두 도는 데 그 정점의 차수만큼 시간이 듭니다. **인접 행렬**은 V x V 크기의 2차원 배열로 두 정점 사이의 간선 유무를 0/1로 적어 두는 형태입니다. 공간이 O(V^2)이며 정점 간 간선 존재를 O(1)에 묻을 수 있습니다. 코딩 인터뷰의 거의 모든 문제는 V가 E에 비해 크지 않으므로 인접 리스트가 정석입니다. 인접 행렬은 V가 작고 간선이 빽빽한 경우에만 유리합니다.

이제 **DFS로 사이클 탐지**를 봅니다. 방향 그래프에서의 사이클 탐지가 가장 자주 묻는 형태입니다. 각 정점에 대해 '아직 안 가 봄', '지금 가는 중', '다 가 봄'의 세 상태를 두고, '지금 가는 중'인 정점을 다시 만나면 그 시점에 사이클이 발견된 것입니다. 무방향 그래프의 사이클 탐지는 더 단순한데, DFS로 가다가 부모가 아닌 이미 방문된 이웃을 만나면 사이클입니다.

```python
def has_cycle_directed(graph: dict[int, list[int]]) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {u: WHITE for u in graph}

    def dfs(u: int) -> bool:
        color[u] = GRAY
        for v in graph[u]:
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    return any(dfs(u) for u in graph if color[u] == WHITE)
```

시간은 O(V + E), 공간은 재귀 깊이만큼 O(V)입니다. 큰 V에서는 재귀 깊이 한도를 늘리거나 반복 DFS로 갈아탑니다.

**BFS로 최단 경로**는 가중치가 없는 그래프에서 가장 자주 쓰는 풀이입니다. 시작점에서 각 정점까지의 간선 수의 최솟값이 답이며, BFS가 정점을 만나는 순간 그 거리가 곧 최단 거리입니다. 큐에서 한 번 꺼낸 정점은 다시 갱신될 일이 없으므로 visited 집합 하나로 충분합니다. 가중치가 있는 그래프라면 다익스트라(우선순위 큐 + BFS의 결합)로 넘어가야 합니다.

```python
from collections import deque

def shortest_path(graph: dict[int, list[int]], src: int, dst: int) -> int:
    if src == dst:
        return 0
    q = deque([(src, 0)])
    visited = {src}
    while q:
        u, d = q.popleft()
        for v in graph[u]:
            if v == dst:
                return d + 1
            if v not in visited:
                visited.add(v)
                q.append((v, d + 1))
    return -1
```

다음 도구는 **Union-Find**, 다른 이름으로 Disjoint Set Union(DSU)입니다. 정점들을 여러 집합으로 묶고, 두 집합을 합치는 연산(union)과 어떤 정점이 어느 집합에 속하는지를 묻는 연산(find)을 빠르게 제공하는 자료구조입니다. 각 집합을 대표하는 '루트' 정점을 두고, 정점마다 자기 부모를 기록한 배열을 들고 다닙니다. find는 부모를 따라 올라가 루트를 찾고, union은 두 루트를 한쪽으로 붙입니다.

두 최적화가 표준입니다. 첫째는 **경로 압축**으로, find를 따라 올라가면서 거쳐 간 모든 정점의 부모를 루트로 바로 갱신하는 기법입니다. 둘째는 **랭크 또는 크기에 의한 병합**으로, 두 집합을 합칠 때 작은 쪽을 큰 쪽 아래에 붙여 트리가 한쪽으로 늘어지지 않게 합니다. 두 최적화를 모두 적용하면 한 연산의 amortized 시간이 거의 O(1)에 가까운 역 아커만 함수 α(n) 수준으로 떨어집니다.

```python
class DSU:
    def __init__(self, n: int):
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1
        return True
```

Union-Find의 대표 응용은 무방향 그래프의 **연결 요소 개수** 세기, **Kruskal 최소 신장 트리**, **사이클 검출**(같은 집합에 속한 두 정점을 잇는 간선이 발견되면 사이클)입니다. 동적으로 간선이 추가되는 상황에서 사이클 발생 여부를 빠르게 알고 싶을 때 Union-Find가 사실상 유일한 선택지입니다.

마지막 도구는 **위상 정렬**입니다. 방향 그래프에서 모든 간선이 '앞에서 뒤로'를 가리키게 정점을 한 줄로 나열하는 정렬이며, 사이클이 있으면 존재하지 않습니다. 강의 선후수 관계, 빌드 의존성 같은 문제의 골격입니다.

두 구현이 있습니다. 첫 번째는 **Kahn 알고리즘**, 두 번째는 **DFS 기반**입니다. Kahn은 진입 차수(in-degree)가 0인 정점들을 큐에 넣고 하나씩 꺼내며 그 정점이 가리키던 이웃의 진입 차수를 1씩 줄여, 새로 0이 된 이웃을 큐에 넣는 방식입니다. 모두 꺼낸 결과의 길이가 V보다 작으면 사이클이 있고, 같으면 그 순서가 위상 정렬입니다.

```python
from collections import deque

def topo_sort(graph: dict[int, list[int]], n: int) -> list[int]:
    indeg = [0] * n
    for u in graph:
        for v in graph[u]:
            indeg[v] += 1
    q = deque([u for u in range(n) if indeg[u] == 0])
    out: list[int] = []
    while q:
        u = q.popleft()
        out.append(u)
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return out if len(out) == n else []
```

DFS 기반 위상 정렬은 postorder로 정점을 끝낸 순서를 모은 뒤 뒤집는 방식입니다. 코드는 더 짧지만, 사이클 처리를 위해 위에서 본 3색 마킹을 함께 써야 합니다.

도구별 시간/공간과 대표 문제를 한 표로 정리합니다.

```
도구           | 시간       | 공간   | 대표 문제(LeetCode)
DFS 사이클     | O(V + E)   | O(V)   | Course Schedule (207)
BFS 최단 경로  | O(V + E)   | O(V)   | Rotting Oranges (994)
Union-Find     | O(α(n))/op | O(V)   | Number of Provinces (547)
위상 정렬      | O(V + E)   | O(V)   | Course Schedule II (210)
```

어떤 도구를 고를지의 결정 흐름은 다음과 같습니다.

```
가중치 있음? ───── yes ─→ 다익스트라(우선순위 큐 + BFS)
   ↓ no
방향성 있음? ──── yes ─→ 사이클 탐지/순서 → DFS 또는 위상 정렬
   ↓ no
동적 간선 추가? ─ yes ─→ Union-Find
   ↓ no
최단 거리? ──── yes ─→ BFS
   ↓ no
연결성·도달성 ────────→ DFS 또는 BFS
```

함정 세 가지로 마무리합니다. 첫 번째 함정은 **무방향 그래프에서 부모 처리**입니다. DFS로 무방향 그래프를 돌 때 직전 부모를 무시하지 않으면 부모를 사이클로 오인합니다. 두 번째 함정은 **격자에서의 방문 표시 갱신**입니다. 격자도 그래프이며 각 칸이 정점, 상하좌우 이웃이 간선입니다. visited를 갱신하는 시점을 큐에 넣을 때로 잡지 않고 큐에서 꺼낼 때로 잡으면 같은 칸이 여러 번 큐에 들어가 메모리가 폭주합니다. 세 번째 함정은 **Union-Find의 find 안 경로 압축 누락**입니다. 경로 압축이 없으면 트리가 한쪽으로 쏠려 연산이 O(log n)이나 O(n)까지 늘어집니다. 면접에서 'amortized α(n)'을 답하려면 경로 압축이 코드에 들어 있어야 합니다.

가중치 그래프의 단일 출발 최단 거리는 다익스트라이고, 음수 간선이 섞이면 벨만-포드, 모든 쌍 최단 거리는 플로이드-워셜로 갈라지지만, 코딩 인터뷰 Medium 단계에서는 이 정도 분기까지는 잘 묻지 않습니다. 도구 네 가지를 깊이 익혀 두는 것이 우선입니다.

정리하면, 그래프 문제는 인접 리스트로 표현하고, DFS·BFS·Union-Find·위상 정렬 네 도구로 거의 모두 풀립니다. DFS는 사이클 탐지와 연결성, BFS는 최단 거리, Union-Find는 동적 연결 요소, 위상 정렬은 의존성 순서가 각각의 강점입니다. 가중치가 들어오면 다익스트라로 넘어가고, 격자 문제는 visited 갱신 시점을 큐 삽입 시로 잡습니다.

다음 단원인 2.3.3에서는 점화식과 메모이제이션·타뷸레이션으로 풀어 내는 동적 계획법을 다루며, 1D/2D DP와 Knapsack, LIS의 골격을 정리합니다.
