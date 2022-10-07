def lengthOfLongestSubstring(s):
    ans = 0
    stack = []
    for i in s:
        if i in stack:
            stack = stack[stack.index(i) + 1 :]
        stack.append(i)
        if len(stack) > ans:
            ans = len(stack)
    return ans


s = ""
print(lengthOfLongestSubstring(s))
