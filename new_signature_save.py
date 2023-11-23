# from py_mini_racer import py_mini_racer
#
# # Define the JavaScript code as a string
# js_code = """
# Date = undefined
# Math.random = undefined
#
# const token = {
#     burn_percentage: 0.5,
#     get_burn_amount(amount) {
#         return amount * token.burn_percentage
#     },
#     rng() {
#         return ":("
#     }
# };
# """
#
# # Create an instance of MiniRacer
# ctx = py_mini_racer.MiniRacer()
#
# # Evaluate the JavaScript code
# ctx.eval(js_code)
#
# # Call the add function from the MyClass object
# result = ctx.call("token.rng")
# print(result)  # Output: 8

data = [
        {"data": "abc", "type": "type1"},
        {"data": "capybara", "type": "type2"}
    ]

sorted_data = {}

for obj in data:
    obj_type = obj["type"]
    if obj_type in sorted_data:
        sorted_data[obj_type].append(obj)
    else:
        sorted_data[obj_type] = [obj]

print(sorted_data)
