from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
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
        slowmo=10,
    )
    open_robot_order_website()
    download_csv_file()
    fill_form_with_csv()
    archive_receipts()

    
def open_robot_order_website():
    """
    Navigates to the given URL
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_csv_file():
    """
    Downloads the csv file from given URL
    """
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    """
    Returns the orders from the website
    """
    library = Tables()
    orders = library.read_table_from_csv("orders.csv", header=True)
    return orders

def close_annoying_modal():
    """
    Open the order page and accept the warning
    """
    page = browser.page()
    page.click("text=Yep")

def fill_and_submit_csv_data(row):
    """
    Fills the csv data and places the order
    """
    filesystem = FileSystem()
    page = browser.page()
    close_annoying_modal()
    head_index = row[1]
    body_index = row[2]
    page.select_option("#head" , index=int(head_index))
    page.click("css=#id-body-" + body_index)
    page.fill("css=input[placeholder='Enter the part number for the legs']", row[3])
    page.fill("#address", row[4])
    page.click("button:text('Preview')")
    page.click("button:text('ORDER')")
    while page.is_visible("css=.alert-danger"):
        page.click("button:text('ORDER')")

    pdf_stored = store_receipt_as_pdf(row[0])
    screenshot = screenshot_robot(row[0])
    embed_ss_to_receipt(screenshot, pdf_stored)
    filesystem.remove_file(screenshot)

    page.click("button:text('ORDER ANOTHER ROBOT')")

def fill_form_with_csv():
    """
    Loop over the orders and fill the form
    """    
    for i in range(len(get_orders())):
        fill_and_submit_csv_data(get_orders()[i])

def store_receipt_as_pdf(order_number):
    """
    Export the receipt as a pdf file.
    """
    page = browser.page()
    receipt_html = page.locator("#order-completion").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, "output/results/receipt_"+order_number+".pdf")
    return "output/receipt_"+order_number+".pdf"

def screenshot_robot(order_number):
    """
    Take a screenshot of the page
    """
    page = browser.page()
    page.screenshot(path="output/results/screenshot_robot_"+order_number+".png")
    return "output/results/screenshot_robot_"+order_number+".png"

def embed_ss_to_receipt(screenshot, pdf_file):
    file_paths = [screenshot]
    pdf = PDF()
    pdf.add_files_to_pdf(
        files = file_paths,
        target_document = pdf_file,
        append = True
    )

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("output/results", "receipts_zip.zip")




