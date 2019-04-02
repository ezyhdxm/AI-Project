class Solution:
    def distributeCoins(self, root: 'TreeNode') -> 'int':
        prev = {}
        prev[root] = None
        count = 0
        def BFS(v):
            queue = [v]
            dep = 1
            while queue:
                u = queue.pop(0)
                if u.val > 0:
                    u.val -= 1
                    return dep
                if u.left!=None:
                    if u.left not in queue:
                        queue.append(u.left)
                if u.right!=None:
                    if u.right not in queue:
                        queue.append(u.right)
                if prev[u]!=None:
                    if prev[u] not in queue:
                        queue.append(prev[u])
                dep += 1
    
        def explore(v,count):
            if (v.left==None)&(v.right==None):
                if v.val>=1:
                    count+=v.val-1
                    prev[v].val+=v.val-1
                else:
                    if prev[v].val>=1:
                        count+=1
                        prev[v].val-=1
                    else:
                        count += BFS(prev[v])
                if v == prev[v].left:
                    prev[v].left == None
                else:
                    prev[v].right == None
                return True
            
            if v.right != None:
                prev[v.right] = v
                explore(v.right,count)
                while v.right!=None:
                    explore(v.right,count)            
            if v.left != None:
                prev[v.left] = v
                explore(v.left,count)
                while v.left!=None:
                    explore(v.left,count)
            return
        
        explore(root,count)
        return count

def stringToTreeNode(input):
    input = input.strip()
    input = input[1:-1]
    if not input:
        return None

    inputValues = [s.strip() for s in input.split(',')]
    root = TreeNode(int(inputValues[0]))
    nodeQueue = [root]
    front = 0
    index = 1
    while index < len(inputValues):
        node = nodeQueue[front]
        front = front + 1

        item = inputValues[index]
        index = index + 1
        if item != "null":
            leftNumber = int(item)
            node.left = TreeNode(leftNumber)
            nodeQueue.append(node.left)

        if index >= len(inputValues):
            break

        item = inputValues[index]
        index = index + 1
        if item != "null":
            rightNumber = int(item)
            node.right = TreeNode(rightNumber)
            nodeQueue.append(node.right)
    return root

def main():
    import sys
    import io
    def readlines():
        for line in io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8'):
            yield line.strip('\n')

    lines = readlines()
    while True:
        try:
            line = next(lines)
        root = stringToTreeNode(line);

        ret = Solution().distributeCoins(root)

        out = str(ret);
        print(out)
        except StopIteration:
            break

if __name__ == '__main__':
    main()