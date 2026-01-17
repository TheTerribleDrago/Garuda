import basic

while True:
    text = input("Basic > ")
    result, error = basic.run(text)

    if error:
        print(error)
    elif result is not None:
        print(result)
