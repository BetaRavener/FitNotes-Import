# FitNotes-Import
This simple utility allows FitNotes users to share their routines through backups. 

## Usecase
You want to exchange routines with your friend. First both of you should use backup feature in FitNotes to create backup files. Ask your friend to send you his backup and save it on PC. Then transfer your own backup to the same machine. Run `main.py` script with arguments as shown below, where the first argument is your friend's backup and second is your own backup. The script will list all of your friend's routines. Select the one you'd like to import by entering coresponding number. Because FitNotes doesn't have large common database of exercises, there might be some exercises missing in your backup that your friend created. The comparison is done by exercise name. You can either import his exercise (input `-1`) or select your existing exercise from presented list that matches the one missing. The same is true for exercise categories. Once all missing items are imported, the routine itself along with it's subitems (sections, exercises, sets) is imported.

After successful import you can take your new backup file (which was the second argument) and put it back into FitNotes backup folder on mobile phone. Then choose restore feature to bring data from that backup into the app.

### Usage
`main.py routine_source_backup.fitnotes destination_backup.fitnotes`

## Disclaimer
I'm not responsible for any damage done by using this utility. Always have a copy of unmodified backup somewhere around in case the utility will corupt the data.

## Known issues
Supersets in routines are not yet transfered between backups. There is some abiguity in how these data are stored which would require some testing. Until then, it's fairly easy to add supersets manually afterwards. 
