from gui import MainWindow


class Application:
    """
    Application class to run GUI and rest of code
    """
    def __init__(self):
        w = MainWindow()
        w.title("Welcome to Abalone")
        w.geometry('1150x800')
        w.configure(bg='#FFFAF0')
        w.mainloop()


def main():
    app = Application()


if __name__ == '__main__':
    main()
