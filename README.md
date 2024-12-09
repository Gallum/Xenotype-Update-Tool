# Xenotype-Update-Tool
Python code to update a rimworld xenotype from 1.4 to 1.5 compatibility. 

Included is a single file: update_xenotype_mod.py

This python script will be placed in the root directory for you mod (includes folders such as "About" and "1.4").
For the script to run successfuly, the following directories are REQUIRED: 1.4, About

The Script will create a new directory "1.5" where the contents of the 1.4 folder are copied over, adjusted with necessary changes required in 1.5
It will also create a "backup.zip" file containing the initial backup of 1.4 and About folders. This will either be used by the script to roll back your mod in case of an error, or it can be manually used to roll your mod back.

The Script will also create "backup rev 00.zip" and "results 00.zip" files each time it is run to backup existing files and output new files in a zip format for debugging. 

It will also create a "1.5_update_log.txt" file that will include changes made during the update process.

It will also add a 1.5 version to your About.xml file to indicate it's compliance with rimworld 1.5

If there are any issues, provide the results file for debugging, or, alternatively, the problems should be diagnosable by providing the update_xenotype_mod.py as well as the results zip file to ChatGPT if you have no experience with python.

This script tool was created by me initially, but meticulously refined using ChatGPT 4o such that it is basically fully generated, tested, and verified by an AI such that it should be easily adjustable by ChatGPT or any AI that is refined at producing python code.

It should work to update any Xenotype mod from 1.4 to 1.5


*IF I MISSED ANYTHING PLEASE LET ME KNOW*
This tool should work to update any Xenotype mod to be basically compatible with 1.5, but I am not intimately familiar with the update and based this tool off of information I could find and changes I percieved would need to be made. If I missed a necessary change please let me know so I can adjust the script to account for these necessary changes.
