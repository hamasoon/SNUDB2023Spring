def infix_to_postfix(expression):
    # 연산자 우선순위 설정
    precedence = {'NOT': 3, 'AND': 2, 'OR': 1}
    
    # 후위 표기법으로 변환된 결과를 저장할 리스트
    postfix = []
    
    # 스택을 이용한 변환 과정
    stack = []
    
    for token in expression.split():
        if token in ['AND', 'OR', 'NOT']:
            # 연산자인 경우 스택에서 우선순위가 더 높거나 같은 연산자를 pop하여 결과에 추가
            while stack and stack[-1] != '(' and precedence[stack[-1]] >= precedence[token]:
                postfix.append(stack.pop())
            stack.append(token)
        elif token == '(':
            # 여는 괄호인 경우 스택에 추가
            stack.append(token)
        elif token == ')':
            # 닫는 괄호인 경우 여는 괄호를 만날 때까지 스택에서 pop하여 결과에 추가
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()  # 여는 괄호를 스택에서 제거
        else:
            # 피연산자인 경우 결과에 추가
            postfix.append(token)
    
    # 스택에 남은 모든 연산자를 결과에 추가
    while stack:
        postfix.append(stack.pop())
    
    # 후위 표기법으로 변환된 결과 반환
    return ' '.join(postfix)


def evaluate_postfix(postfix_expression):
    stack = []
    
    for token in postfix_expression.split():
        if token in ['AND', 'OR', 'NOT']:
            # 연산자인 경우 스택에서 피연산자를 pop하여 연산 후 결과를 스택에 push
            operand2 = stack.pop()
            if token == 'NOT':
                # NOT 연산 처리
                result = not operand2
            else:
                operand1 = stack.pop()
                if token == 'AND':
                    # AND 연산 처리
                    result = operand1 and operand2
                elif token == 'OR':
                    # OR 연산 처리
                    result = operand1 or operand2
            stack.append(result)
        else:
            # 피연산자인 경우 스택에 push
            stack.append(bool(token))
    
    # 최종 결과 반환
    return stack[0]


# 테스트 예시
expression = '( A OR B ) AND ( C AND NOT D )'
postfix_expression = infix_to_postfix(expression)

print(f'후위 표기법: {postfix_expression}')
