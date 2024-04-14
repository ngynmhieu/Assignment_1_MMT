from torrent import *

# location = []
# def ask_user_to_choose_location():
#     root = Tk()
#     root.after(0, lambda: open_directory(root, location))
#     root.mainloop()
#     if location:  # Check if the list is not empty
#         return location
#     else:
#         print("No directory selected.")
#         return None
while True:
    create_Torrent_full()
    answer = input("Do you want to continue (Y/N)?\n")
    if (answer.lower() == 'n'):
        break
    elif (answer.lower() == 'y'):
        continue
    else:
        print("Invalid answer, please try again.")
        continue
# filepath = import_file()
# torrent = read_torrent_file(filepath)
# print (torrent.get_info())
# print (len(torrent.get_pieces()))
# hash = torrent2hash(torrent.get_info())
# location = ask_user_to_choose_location()
# verify_data_left(location, torrent)
# print (torrent.get_left())
# print (torrent.get_info())