from robocorp.tasks import task
from robocorp import browser
from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive
from RPA.FileSystem import FileSystem
@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=0,
    )
    open_robot_order_website()
    download_orders()
    fill_robot_forms_with_csv()
    archive_receipts()
def open_robot_order_website():
    """ Open the Robor Spare Bins website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
def get_orders():
    """ Return the orders from the website"""
    library = Tables()
    orders = library.read_table_from_csv(
    "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    return orders
def download_orders():
    """Downloads CSV file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
def close_annoying_modal():
    """ Log in the page and accept the warning"""
    page = browser.page()
    page.click("text=Yep")
def fill_the_form(row):
    filesystem = FileSystem()
    close_annoying_modal()
    page = browser.page()
    head_index = row[1]
    body_index = row[2]
    page.select_option("#head", index=int(head_index))
    page.click("css=#id-body-" + body_index)
    page.fill("css=input[placeholder='Enter the part number for the legs']", row[3])
    page.fill("#address", row[4])
    page.click("button:text('Preview')")
    page.click("button:text('ORDER')")
    while page.is_visible("css=.alert-danger"):
        page.click("button:text('ORDER')")
    pdf_stored = store_receipt_as_pdf(row[0])
    screenshot = screenshot_robot(row[0])
    embed_screenshot_to_receipt(screenshot, pdf_stored)
    filesystem.remove_file(screenshot)
    page.click("button:text('ORDER ANOTHER ROBOT')")
def fill_robot_forms_with_csv():
    """ Loop over the whole order and fill the form"""
    for i in range(len(get_orders())):
        fill_the_form(get_orders()[i])
def store_receipt_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    sales_results_html = page.locator("#order-completion").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, "C:\\Users\\PedroLavinNexler\\Documents\\robot-maker-pdf\\output\\receipts\\completed_order_" + order_number + ".pdf")
    return "C:\\Users\\PedroLavinNexler\\Documents\\robot-maker-pdf\\output\\receipts\\completed_order_" + order_number + ".pdf"
def screenshot_robot(order_number):
    """Take a screenshot of the page"""
    page = browser.page()
    # page.screenshot(path="output/screenshot_robot_" + order_number + ".png")
    page.screenshot(path='C:\\Users\\PedroLavinNexler\\Documents\\robot-maker-pdf\\output\\receipts\\screenshot_robot_' + order_number + ".png")
    return 'C:\\Users\\PedroLavinNexler\\Documents\\robot-maker-pdf\\output\\receipts\\screenshot_robot_' + order_number + ".png"
def embed_screenshot_to_receipt(screenshot, pdf_file):
    file_paths = [screenshot
    ]
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=file_paths,
        target_document=pdf_file,
        append=True
    )
def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('C:\\Users\\PedroLavinNexler\\Documents\\robot-maker-pdf\\output\\receipts', 'receipts_zip.zip')