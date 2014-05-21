from blinker import signal

split_image = signal('split_image')
detect_rows = signal('detect_rows')
detect_columns = signal('detect_columns')
extract_image = signal('extract_image')
image_text = signal('image_text')
