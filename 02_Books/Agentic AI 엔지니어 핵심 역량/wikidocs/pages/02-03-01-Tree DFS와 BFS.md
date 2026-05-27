# 2.3.1 Tree DFS와 BFS

이진 트리의 깊이 구하기, 두 노드의 가장 가까운 공통 조상 찾기, 트리를 문자열로 직렬화하기 같은 문제는 코딩 인터뷰의 가장 자주 나오는 골격 중 하나입니다. 모두 트리의 모든 노드를 적절한 순서로 방문하는 순회의 변형이며, 사고의 결은 깊이 우선 탐색(DFS)이거나 너비 우선 탐색(BFS) 둘 중 하나입니다. 이 단원에서는 트리의 네 가지 순회를 정리하고, 각 순회가 어떤 문제에 맞물리는지를 본 다음, 재귀와 반복 두 구현 방식을 비교합니다.

먼저 용어를 풀어 두겠습니다. **이진 트리**는 각 노드가 왼쪽 자식과 오른쪽 자식 두 개 이하를 갖는 트리입니다. 노드는 보통 val, left, right 세 필드를 가진 객체입니다. **DFS**는 한 자식을 끝까지 따라 내려간 뒤 돌아와 다른 자식으로 가는 탐색 방식이고, **BFS**는 같은 깊이의 노드들을 모두 본 뒤 한 깊이 더 내려가는 탐색 방식입니다.

DFS에는 노드를 방문하는 시점에 따라 세 가지 순회가 있습니다. **preorder**는 노드를 먼저 처리한 뒤 왼쪽, 오른쪽 순서로 내려가고, **inorder**는 왼쪽을 끝까지 내려간 뒤 노드를 처리하고 오른쪽으로 가며, **postorder**는 양쪽 자식을 다 처리한 뒤에야 노드를 처리합니다. BFS에 해당하는 순회는 **level-order**로, 깊이별로 한 층씩 처리합니다.

```
          1
         / \
        2   3
       / \
      4   5

preorder:   1 2 4 5 3
inorder:    4 2 5 1 3
postorder:  4 5 2 3 1
level:      1 2 3 4 5
```

각 순회가 어떤 문제에 맞물리는지가 핵심입니다. preorder는 트리의 구조를 출력하거나 트리를 다른 형태로 복사할 때 자연스럽습니다. 노드 정보를 먼저 받아 두면 자식들이 들어갈 자리도 함께 만들 수 있기 때문입니다. inorder는 이진 탐색 트리에서 값을 오름차순으로 꺼낼 때 가장 적합합니다. postorder는 자식의 결과를 모두 모은 뒤 노드 자신의 결과를 정해야 할 때 쓰입니다. 트리의 깊이, 노드 수, 합 같은 누적 계산이 모두 postorder의 영역입니다.

DFS 구현은 재귀가 가장 직관적입니다. 트리의 깊이를 구하는 함수는 다음과 같이 짧게 끝납니다.

```python
def max_depth(root) -> int:
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

이 함수는 postorder의 골격을 그대로 닮았습니다. 자식 둘의 결과를 먼저 구한 뒤 노드 자신의 답을 그 위에 한 줄 더해 만듭니다. 재귀의 시간은 O(n)이고, 공간은 트리의 깊이만큼 호출 스택을 씁니다. 균형 트리라면 O(log n), 한쪽으로 치우친 트리라면 O(n)입니다.

반복 DFS는 명시적인 스택을 들고 다니는 형태입니다. 재귀 호출이 깊어 스택 오버플로 위험이 있을 때 쓰는 우회이며, 면접에서 한 번씩 요구합니다. preorder의 반복 구현은 다음과 같습니다.

```python
def preorder(root) -> list[int]:
    out: list[int] = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return out
```

오른쪽 자식을 먼저 스택에 넣는 이유는, 스택이 LIFO라 왼쪽이 먼저 꺼내지게 하기 위해서입니다. inorder의 반복 구현은 한 줄 더 길고, postorder의 반복 구현은 가장 까다롭습니다. 면접에서는 inorder까지가 자주 묻고 postorder는 드뭅니다.

BFS는 큐를 들고 다니는 형태가 표준입니다. collections.deque를 쓰며, 한 층씩 모아 처리하는 형태가 가장 자주 쓰입니다.

```python
from collections import deque

def level_order(root) -> list[list[int]]:
    out: list[list[int]] = []
    if root is None:
        return out
    q = deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        out.append(level)
    return out
```

여기서 for _ in range(len(q))의 의도는 '이번 반복을 시작할 때 큐에 있던 노드들만 한 층으로 묶기'입니다. 안에서 자식을 큐에 추가하지만 len(q)는 반복 시작 시점에 이미 고정되어 있으므로 다음 층 노드들은 다음 while 반복에서 처리됩니다.

BFS가 진가를 보이는 자리가 **최소 거리** 문제입니다. 시작 노드에서 각 노드까지의 가장 짧은 거리를 묻는 문제에서, 가중치가 없는 트리나 그래프라면 BFS의 방문 깊이가 곧 최소 거리입니다. DFS로는 같은 답을 보장할 수 없습니다.

조금 더 까다로운 응용으로 **LCA**, 즉 두 노드의 가장 가까운 공통 조상을 찾는 문제가 있습니다. 재귀 DFS로 'p와 q를 자식 서브트리에서 찾았는지'를 반환하면 한 함수로 끝납니다. 두 자식 서브트리 모두에서 찾았다면 지금 노드가 LCA이고, 한쪽에서만 찾았다면 그 쪽이 LCA의 후보로 위로 올라갑니다. 시간 O(n), 공간 O(h)입니다. h는 트리 높이입니다.

**트리 직경**은 트리에서 가장 먼 두 노드 사이의 간선 수를 묻는 문제로, 각 노드를 정점으로 삼는 '왼쪽 깊이 + 오른쪽 깊이'의 최댓값이 답입니다. postorder DFS 한 번으로 전역 최댓값을 갱신하며 풀립니다.

**Serialize/Deserialize**는 트리를 문자열로 바꿨다가 다시 트리로 복원하는 문제입니다. preorder로 직렬화하면 'None 자식 표시'만 일관되게 적어 두면 한 번의 순회로 복원이 가능합니다. 여러 면접 문제에서 'tree를 어떻게 저장할 것인가'를 묻는 자리에 자주 나옵니다.

대표 LeetCode 문제 네 개를 외워 둡니다. Maximum Depth of Binary Tree(104), Binary Tree Level Order Traversal(102), Lowest Common Ancestor of a Binary Tree(236), Serialize and Deserialize Binary Tree(297)입니다.

복잡도를 한 표로 정리합니다.

```
문제             | 시간 | 공간(보조) | 자연스러운 순회
최대 깊이        | O(n) | O(h)       | postorder
Level Order      | O(n) | O(w)       | BFS
LCA              | O(n) | O(h)       | postorder
Serialize        | O(n) | O(n)       | preorder
트리 직경        | O(n) | O(h)       | postorder
```

w는 트리의 폭(어떤 깊이의 노드 수의 최대)이고, h는 트리 높이입니다.

함정 세 가지로 마무리합니다. 첫 번째 함정은 **None 자식 처리**입니다. 재귀 DFS에서 base case로 if node is None: return을 빠뜨리면 None.val에서 죽습니다. 두 번째 함정은 **재귀 깊이 제한**입니다. 파이썬의 기본 재귀 한도는 1000인데, 노드 수가 10만 이상인 입력에서는 한쪽으로 치우친 트리가 들어오면 한도를 넘어 RecursionError가 납니다. sys.setrecursionlimit으로 한도를 올리거나 반복 구현으로 바꿉니다. 세 번째 함정은 **BFS의 층 묶기**입니다. for _ in range(len(q))를 빠뜨리고 그냥 while q로 모든 노드를 한 줄로 펴면, 결과는 같지만 층별 정보가 사라집니다. 층별 출력이 필요한 문제에서는 이 구조를 꼭 챙깁니다.

DFS와 BFS의 선택 기준을 한 줄로 정리하면, 트리의 모양을 그대로 따라가며 자식의 결과를 모아야 하면 DFS, 깊이별로 균등하게 보거나 최소 거리를 묻는다면 BFS입니다. 둘 다 시간 O(n)이라는 점은 같습니다.

정리하면, 트리의 순회는 preorder, inorder, postorder의 DFS 세 가지와 level-order의 BFS 한 가지로 나뉩니다. 깊이·LCA·직경은 postorder 골격, 직렬화는 preorder, 최소 거리는 BFS가 자연스럽습니다. 재귀가 직관적이지만 깊이가 커질 가능성이 있으면 반복 구현으로 갈아탑니다.

다음 단원인 2.3.2에서는 트리에서 그래프로 확장해, 인접 리스트 vs 행렬, 사이클 탐지, 최단 경로, Union-Find, 위상 정렬까지를 한 번에 다룹니다.
