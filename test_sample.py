# test_sample.py

# Hard-coded password (should be flagged by AI)
PASSWORD = "123456"

def insecure_eval(user_input):
    # Using eval is dangerous
    return eval(user_input)

def main():
    user_input = "2 + 2"
    print(insecure_eval(user_input))

main()
