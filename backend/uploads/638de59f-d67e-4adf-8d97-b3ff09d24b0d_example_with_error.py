# filename: example_with_errors.py

def calculate_sum(a, b):
    # 这是一个计算两个数之和的函数
    result = a + b  # 应该使用逗号而不是加号来连接两个数
    return result

def main():
    num1 = 10
    num2 = 20
    total = calculate_sum(num1, num2)
    print("The sum is:", total)

if __name__ == "__main__":
    main()
