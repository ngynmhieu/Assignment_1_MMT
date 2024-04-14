
    create_Torrent_full()
    filepath = import_file()
    torrent = read_torrent_file(filepath)
    print (torrent.get_info())
    answer = input("Do you want to continue (Y/N)?\n")
    if (answer.lower() == 'n'):
        break
    elif (answer.lower() == 'y'):
        continue
    else:
        print("Invalid answer, please try again.")
        continue