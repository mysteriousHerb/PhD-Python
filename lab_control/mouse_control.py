import pyautogui  # http://pyautogui.readthedocs.io/en/latest/cheatsheet.html
import time


def system_setup():
    pyautogui.FAILSAFE = True

def record_image():
    '''Record any image from screen to later come back'''
    crop_size = 100 # Higher value, higher sensitivity
    pyautogui.moveTo(pyautogui.size()[0], 0) # move mouse out of window
    # Take a screenshot without mouse on any button
    screenshot_full= pyautogui.screenshot('screenshot_full.png')
    if pyautogui.confirm(
        '''Move mouse to memoriable location.\n
        Press enter to memorise the screen crop of this area''') == 'Cancel':
        raise SystemExit # if user click "Cancel", stop whole program
    mouse_position = pyautogui.position()
    crop_region = (
        int(mouse_position[0]-crop_size/2),
        int(mouse_position[1]-crop_size/2),
        int(mouse_position[0]+crop_size/2),
        int(mouse_position[1]+crop_size/2))
    screenshot_crop = screenshot_full.crop(crop_region)
    screenshot_crop.save('screenshot_crop.png')
    return screenshot_crop

def record_mouse_position():
    if pyautogui.confirm(
        '''Move mouse to memoriable location.\n
        Press enter to memorise the location''') == 'Cancel':
        raise SystemExit
    recorded_mouse_position = pyautogui.position()
    return recorded_mouse_position

def move_to_recorded_position(record):
    if type(record) is tuple:
        pass
    else:
        record = pyautogui.locateCenterOnScreen('screenshot_crop.png')
    pyautogui.moveTo(record[0], record[1], 0.2)
    time.sleep(0.5)
    pyautogui.click()

def record_filepath():
    folder = pyautogui.prompt(title='Paste the filepath here.', default=r'C:\Users\herbz')
    if folder is None:
        raise SystemExit
    filename = pyautogui.prompt(title='type filename here', default=r'20x-TL-CP-001.jpg')
    if folder is None:
        raise SystemExit
    image_number = int(filename[-7:-4])
    return folder, filename, image_number

def save_to_file(folder, filename, image_number):
    filename = filename[:-8]
    filepath = folder + r'/' +filename +'-{:03}'.format(image_number) + '.jpg'
    secs_between_keys = 0.05
    pyautogui.hotkey('ctrl','a')
    pyautogui.hotkey('delete')
    pyautogui.typewrite(filepath+'\n', interval = secs_between_keys)
    print(filepath)

def time_lapse(repeat_times = 5, time_intervals = 1, wait_time = 1):
    recorded_item = pyautogui.confirm(text = 'Record item is a ?', buttons=['image', 'location', 'Cancel'])
    if recorded_item == 'image':
        recorded_item = record_image()
    elif recorded_item == 'location':
        recorded_item = record_mouse_position()
    else:
        raise SystemExit
    folder, filename, image_number = record_filepath()
    for i in range(repeat_times):
        time.sleep(time_intervals)
        print('Taking actions. Get away from keyboard please!')
        time.sleep(wait_time)
        move_to_recorded_position(recorded_item)
        save_to_file(folder, filename, image_number)
        pyautogui.moveTo(pyautogui.size()[0], 0) # move mouse out of window
        image_number +=1

if __name__ == '__main__':
    system_setup()
    time_lapse(repeat_times = 5, time_intervals = 2, wait_time = 0.5)
    

    


