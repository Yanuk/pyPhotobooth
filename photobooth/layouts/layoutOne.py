import cv
import os

NUM_IMAGES = 1
FINAL_IMG_WIDTH = 3000
FINAL_IMG_HEIGHT = 2000

FINAL_IMG_QR_CODE_X = 1400
FINAL_IMG_QR_CODE_Y = 1735
FINAL_IMG_DIVIDER_WIDTH = 2     # even number
FINAL_IMG_DISPLAY_SIZE = 0.33

FINAL_IMG_BORDER_WIDTH_TOP = 91
FINAL_IMG_BORDER_WIDTH_BOTTOM = 0
FINAL_IMG_BORDER_WIDTH_LEFT = 118
FINAL_IMG_BORDER_WIDTH_RIGHT = 95

# border-less (not tested)
#FINAL_IMG_BORDER_WIDTH_TOP = 36
#FINAL_IMG_BORDER_WIDTH_BOTTOM = 0
#FINAL_IMG_BORDER_WIDTH_LEFT = 36
#FINAL_IMG_BORDER_WIDTH_RIGHT = 36

##############################################################################
def OnlyOne(images, logoFile, qrImg):
    
    p1 = images[0]
    
    border_top = FINAL_IMG_BORDER_WIDTH_TOP
    border_bottom = FINAL_IMG_BORDER_WIDTH_BOTTOM
    border_left = FINAL_IMG_BORDER_WIDTH_LEFT
    border_right = FINAL_IMG_BORDER_WIDTH_RIGHT
    divider_width = FINAL_IMG_DIVIDER_WIDTH
    
    pic_widths = p1.width
    pic_heights = p1.height
    #print "orig w %d h %d" % (pic_widths, pic_heights)
    
    finalImg = cv.CreateImage((FINAL_IMG_WIDTH, FINAL_IMG_HEIGHT), 8, 3)
    cv.Set(finalImg, cv.CV_RGB(255,255,255))
    
    resized_W = int((FINAL_IMG_WIDTH - (border_left+border_right) - (divider_width)) / 2)  
    resized_H = int((float(resized_W)/pic_widths) * pic_heights) 

    # rect = (left, top, width, height)
    # top left
    rect = (border_left, border_top, resized_W * 2, resized_H * 2)
    cv.SetImageROI(finalImg, rect)
    cv.Resize(p1, finalImg)
    cv.ResetImageROI(finalImg)
    
    
    logoImg = None
    if os.path.exists(logoFile):
        logoImg = cv.LoadImage(logoFile, cv.CV_LOAD_IMAGE_COLOR)
        
    if (logoImg is not None):
        rect = (0, 2*resized_H + border_top + divider_width, FINAL_IMG_WIDTH, logoImg.height)
        cv.SetImageROI(finalImg, rect)
        cv.Resize(logoImg, finalImg)
        cv.ResetImageROI(finalImg)
        
    if (qrImg is not None):
        rect = (FINAL_IMG_QR_CODE_X, FINAL_IMG_QR_CODE_Y, qrImg.width, qrImg.height)
        cv.SetImageROI(finalImg, rect)
        cv.Resize(qrImg, finalImg)
        cv.ResetImageROI(finalImg)
        
    return finalImg
