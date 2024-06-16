from ctypes import windll
class Chest():
    def _D__Setup_Chest(self, window, frame):
            from .Tab_Page_Frame import Frame
            self.Window = window
            self.Manager : Frame = frame
            self.PageParent = self.Manager.page_frame
            self.Current_Page = "Get it using the get_current_page() method"
            self.Displayed_Pages = self.Manager.pages_dict
            self.MainPages = self.Manager.mainpages_dict
            self.SubPages = self.Manager.subpages_dict
            self.userPagesDirectory = self.Manager.U_Pages_dir
            self.toolsFrame = self.Manager.apps_frame
            self.Dialog_Manager = self.Manager.dialog_widget
            self.scaleFactor = windll.shcore.GetScaleFactorForDevice(0) / 100

    def get_current_page(self):
        """Returns the Displayed Page name

        Returns:
            str: Displayed Page name
        """
        return self.Manager.page_choise

    def Switch_Page(self, Target_Page: str):
        """Closes the current page and Shows the target page (Only for Global Pages)

        Args:
            Target_Page (str): Name of the target page "case sensitive"
        """
        self.Manager.page_switcher(Target_Page)

    def reload_page(self, name, args):
        """Reloads the page to apply any saved changes made to the code of the page

        Args:
            name (str): Name of the page "case sensitive"
            args (tuple): Arguments to be passed to the page
        """
        self.Manager.reload_page(name, args)

    def Store_a_Page(self, Target_Page: str, Switch=True):
        """Constructs a new main page, so that it is ready to be opened at any moment

        Args:
            Target_Page (str): Name of the target page file (and) class "case sensitive"
            Switch (bool, optional): Switch to that page after importing it or not. Defaults to True.
        """
        self.Manager.new_page_constructor(Target_Page, Switch)

    def Store_SubPage(self, Main_page: str, Sub_page, keep : bool = True, args: tuple = ()):
        """Constructs the Subpage, so that it is ready to be opened at any moment

        Args:
            Main_page (str): used to get the name of the main page class "case sensitive"
            Sub_page (Class): used to initialize the subpage class with the necessary parameters
            keep (bool, optional): keep the subpage if it already exists. Defaults to True.
            args (tuple, optional): arguments to be passed to the subpage. Defaults to ().
        """
        self.Manager.Subpage_Construction(Main_page, Sub_page, keep, args)

    def Use_SubPage(self, Main_page_name: str, Sub_page_name: str):
        """Opens the SubPage

        Args:
            Main_page (str): used to get the name of the main page class "case sensitive"
            Sub_page (str): used to get the name of the sub page class "case sensitive"
        """
        self.Manager.Subpage_init(Main_page_name, Sub_page_name)

    def Return_SubPage(self, Main_page_name: str, Sub_page_name: str):
        """Closes the SubPage

        Args:
            Main_page (str): used to get the name of the main page class "case sensitive"
            Sub_page (str): used to get the name of the sub page class "case sensitive"
        """
        self.Manager.Subpage_return(Main_page_name, Sub_page_name)


userChest = Chest() # the chest object to be used by the user