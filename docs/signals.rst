=======
Signals
=======

split_image
===========

Sent when a cell image is extacted from an image containing a table

*Arguments*:

* input_filename
* input_md5
* filename
* md5
* column
* row
* left
* upper
* right
* lower

extract_image
=============

Sent when an image is extracted from a PDF

*Arguments*:

* input_filename
* input_md5
* filename
* md5
* page
* project

image_text
==========

Sent when text is providef for an image

*Arguments*:

* source_filename
* source_md5
* method
* text
* user

detect_columns
==============

*Arguments*:

* filename
* md5
* columns

detect_rows
==============

*Arguments*:

* filename
* md5
* rows
