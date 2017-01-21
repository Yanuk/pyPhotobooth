import os


def print_image_default_printer(file_name):
    print_image("PDF", file_name)
    
def print_image(printer_name, file_name):
    command = "lpr -P %s %s" % (printer_name, file_name)
    os.system(command) 


