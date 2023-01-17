from serial import Serial


class Tags:
    """
    This class contains object names on the Nextion screen.
    There some pages and some items in the pages.
    """

    class OpeningPage:
        Tag = 'opening'
        HeaderTag = 'header'
        MessageTag = 'message'

    class RegisterPage:
        Tag = 'register'
        HeaderTag = 'header'
        CodeTag = 'code'
        MessageTag = 'message'

    class PurchasePage:
        Tag = 'purchase'
        HeaderTag = 'header'
        NameTag = 'name'
        PriceTag = 'price'
        CodeTag = 'code'
        MessageTag = 'message'


class Display:
    """
    This class represents Nextion display.
    It creates a serial connection and controls pages and items by writing.
    """

    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)

    def __del__(self):
        self.connection.close()

    def _end_of_command(self):
        for i in range(3):
            self.connection.write(b'\xff')

    def update_page(self, page):
        self.connection.write('page {}'.format(page).encode())
        self._end_of_command()

    def update_text(self, tag, text):
        self.connection.write('{}.txt="{}"'.format(tag, text).encode())
        self._end_of_command()


def test():
    try:
        import time

        # display = Display(port='COM7')  # For Windows connected via adapter
        display = Display(port='/dev/ttyUSB0')  # For Linux connected via adapter

        display.update_page(Tags.OpeningPage.Tag)
        display.update_text(Tags.OpeningPage.MessageTag, 'Starting...')
        time.sleep(5)

        display.update_page(Tags.RegisterPage.Tag)
        display.update_text(Tags.PurchasePage.CodeTag, 'This is register page!')
        time.sleep(5)

        display.update_page(Tags.PurchasePage.Tag)
        display.update_text(Tags.PurchasePage.NameTag, 'Old Watch')
        display.update_text(Tags.PurchasePage.PriceTag, '500TL')
        display.update_text(Tags.PurchasePage.CodeTag, 'This is purchase page!')
        time.sleep(5)
    except Exception as exception:
        print(exception)


if __name__ == '__main__':
    test()
