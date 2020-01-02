import hashlib


def get_md5(input_value):
    if isinstance(input_value, str):
        input_value = input_value.encode("utf-8")
    m = hashlib.md5()
    m.update(input_value)
    return m.hexdigest()


# print(get_md5("https;"))
