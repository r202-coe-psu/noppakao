def save_to_file_field(field, data):
    field.delete()
    if type(data) == str:
        data = data.encode("utf-8")
    if data:
        field.new_file()
        field.write(data)
        field.close()
