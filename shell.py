import garuda

while True:
    text = input("Garuda > ")
    result,error = garuda.run(text)
    if error:
        print(error.as_string())
    else:
        print(result)