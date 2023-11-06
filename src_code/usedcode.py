# def authenticate_user(filename, username, password):
#     valid = False
#     with open(filename, "r") as file: 
#         for line in file:
#             parts = line.strip().split()
#             stored_username, stored_password,*awskeys = parts
#             if (username == stored_username) and (password == stored_password):
#                 valid = True
#                 break
#     return valid

     
# except ValueError as ve:
# print(f"Caught a ValueError: {ve}")
# print(f"Please check that the data in password.txt file is formatted correctly")
# break

# except Exception as ex:
# raise Exception(f"An error occurred during authentication: {ex}")