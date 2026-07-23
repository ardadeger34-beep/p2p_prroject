P2P File Sharing Project

## Group Members
- Arda Değer - 2366055
- Mehmet Emre İlter - 2483949
- Tolga Uslu - 2366386

## Platform
macOS

## Requirements
Install required library before running:
pip3 install pyDes

add a file txt or png for demo, there is not one in the folder currently!

## How to Run

Create 2 folder named "chunks" and "logs".

Open 4 separate terminals and run in this order:

Terminal 1 - Chunk Announcer:
python3 "[dr.alex]_chunk_announcer.py"

Terminal 2 - Content Discovery:
python3 "[dr.alex]_chunk_discovery.py"

Terminal 3 - Chunk Uploader:
python3 "[dr.alex]_chunk_uploader.py"

Terminal 4 - Chunk Downloader:
python3 "[dr.alex]_chunk_downloader.py"

After openning the terminals , open terminal 1 (chunk_announcer) , enter your desired username and the file you want to download with it's extensions (like test.txt or image.png).

After entering the file name and username open terminal 4 (chunk_downloader) and follow the instructions that the programs tells.

!! Dont forget the add a file to demo. !!
(you can add a txt file or an image directly and use the [dr.alex]_chunk_announcer.py to create the chunks for you !)

!! All inputs must be the same as how program gives it to you, they are case-sensetive. !!
For example: you have to write "View Contents" or "Download Content" or View History" ( Without "'s ) exactly how it is given by the program, same for Seucre and Unsecure options.

## Can do;
View Contents   - shows files available to download
Download Content - choose a file and download securely or unsecurely.
History         - shows past downloads and its times.

## Limitations
- Downloaded files does not come with .png or .txt extension, you need to add it manually.
- All users must share the same LAN
- Broadcast IP must match your network (currently set to mine on chunk_announcer.py, change it.)