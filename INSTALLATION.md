# Installation — AutoRoute Sync for FL Studio

AutoRoute Sync for FL Studio runs through FL Studio’s MIDI Controller Scripting system. You do not need a physical MIDI keyboard, pad controller, or other MIDI hardware. You only need a free software-only virtual MIDI port so FL Studio can host the script.

Follow the steps for your operating system exactly. The folder name required by this project is:

```text
AutoRouteSync
```

The script file required by this project is:

```text
device_AutoRouteSync.py
```

## Windows installation

### Step 1: Install the free virtual MIDI port

1. Download loopMIDI from its [official website](https://www.tobias-erichsen.de/software/loopmidi.html).
2. Install loopMIDI.
3. Open loopMIDI after installation.
4. In the loopMIDI window, create a new virtual MIDI port.
5. Name the port exactly:

   ```text
   AutoRoute Virtual
   ```

6. Leave loopMIDI running. You may minimize it to the system tray, but do not close it while using FL Studio.

The virtual port does not need to send notes or controller messages. It only provides the software MIDI input that FL Studio uses to load the script.

### Step 2: Find the FL Studio user-data folder

The safest method is to find the folder from inside FL Studio:

1. Open FL Studio.
2. Open **Options > File settings**.
3. Find the field labeled **User data folder**.
4. Note the folder path shown there.
5. Open that folder in Windows File Explorer.

The standard Windows location is usually:

```text
Documents\Image-Line\FL Studio\
```

However, use the exact path shown in your own FL Studio installation if it is different.

### Step 3: Open the Hardware folder

Inside the FL Studio user-data folder, open:

```text
Settings\Hardware\
```

The complete standard path is:

```text
Documents\Image-Line\FL Studio\Settings\Hardware\
```

If the `Hardware` folder does not exist, create it manually:

1. Right-click inside the FL Studio `Settings` folder.
2. Select **New > Folder**.
3. Name the folder exactly:

   ```text
   Hardware
   ```

### Step 4: Create the AutoRouteSync folder

Inside the `Hardware` folder, create a new folder manually:

1. Open the `Hardware` folder.
2. Right-click an empty area.
3. Select **New > Folder**.
4. Name the new folder exactly:

   ```text
   AutoRouteSync
   ```

The final folder path must be:

```text
Documents\Image-Line\FL Studio\Settings\Hardware\AutoRouteSync\
```

Do not put the script directly in the `Hardware` folder. It must be inside the `AutoRouteSync` folder.

### Step 5: Copy the script into AutoRouteSync

1. Open the downloaded AutoRoute Sync ZIP file.
2. Extract it, or open it and locate `device_AutoRouteSync.py`.
3. Copy `device_AutoRouteSync.py`.
4. Paste it into the folder you created:

   ```text
   Documents\Image-Line\FL Studio\Settings\Hardware\AutoRouteSync\
   ```

The final file path must be:

```text
Documents\Image-Line\FL Studio\Settings\Hardware\AutoRouteSync\device_AutoRouteSync.py
```

Do not rename the script. The filename must begin with `device_` and end with `.py`.

### Step 6: Assign the script to the virtual MIDI input

1. Return to FL Studio.
2. Open **Options > MIDI settings**.
3. In the **Input** section, locate `AutoRoute Virtual`.
4. Click `AutoRoute Virtual` to select it.
5. Enable the input device.
6. In the **Controller type** field for that input, select:

   ```text
   Auto-Route & Sync (user)
   ```

7. Assign an unused port number, such as `0`.
8. If `AutoRoute Virtual` also appears in the **Output** section, leave the output disabled unless FL Studio requires it, or assign the same unused port number.

The important part is that the virtual port is enabled in the **Input** section and has `Auto-Route & Sync (user)` selected as its controller type.

### Step 7: Confirm that FL Studio loaded the script

1. Open **View > Script output**.
2. Reload the script if the option is available, or close and reopen FL Studio.
3. Check the output for a successful initialization message such as `init ok`.

If the script name does not appear in the Controller type list, recheck the folder and filename. The required path is:

```text
...\Settings\Hardware\AutoRouteSync\device_AutoRouteSync.py
```

## macOS installation

### Step 1: Enable the built-in virtual MIDI port

macOS includes a software MIDI connection called IAC Driver.

1. Open **Applications > Utilities > Audio MIDI Setup**.
2. From the menu bar, select **Window > Show MIDI Studio**.
3. Double-click **IAC Driver**.
4. Enable **Device is online**.
5. Create or select an IAC bus named:

   ```text
   AutoRoute Virtual
   ```

6. Keep the IAC Driver online while using FL Studio.

### Step 2: Find the FL Studio user-data folder

1. Open FL Studio.
2. Open **Options > File settings**.
3. Find the field labeled **User data folder**.
4. Open the displayed location in Finder.

Use the exact user-data path displayed by your installation. The folder structure inside it must be:

```text
Image-Line/FL Studio/Settings/Hardware/
```

### Step 3: Create the required folders

Inside the FL Studio user-data folder:

1. Open or create the `Settings` folder.
2. Inside `Settings`, open or create the `Hardware` folder.
3. Inside `Hardware`, create a new folder named exactly:

   ```text
   AutoRouteSync
   ```

The final folder must be:

```text
Image-Line/FL Studio/Settings/Hardware/AutoRouteSync/
```

Do not place the script directly in the `Hardware` folder.

### Step 4: Copy the script into AutoRouteSync

Copy the file named `device_AutoRouteSync.py` into:

```text
Image-Line/FL Studio/Settings/Hardware/AutoRouteSync/
```

The final file path must end with:

```text
Settings/Hardware/AutoRouteSync/device_AutoRouteSync.py
```

Do not rename the file.

### Step 5: Assign the script in FL Studio

1. Open FL Studio’s **Options > MIDI settings**.
2. In the **Input** section, select **IAC Driver**.
3. Enable the input.
4. Set **Controller type** to:

   ```text
   Auto-Route & Sync (user)
   ```

5. Assign an unused port number.
6. Reload the script from **View > Script output**, or restart FL Studio.

## Test the installation

After the script is enabled, create a clean test project and perform these tests:

1. Add a new sample directly to the Channel Rack.
2. Confirm that the new channel receives a vivid, non-red color.
3. Confirm that the channel is routed to a free Mixer insert.
4. Confirm that the Mixer insert receives the channel’s name and matching color.
5. Drag another sample or instrument into the Playlist.
6. Confirm that the second channel receives the same automatic organization.
7. Delete one of the automatically managed channels.
8. Wait briefly for FL Studio to finish updating.
9. Confirm that the managed Mixer insert restores the name and color it had before the script claimed it.

## Updating the script

To install a future update:

1. Close the current script file if it is open in a text editor.
2. Download the new `device_AutoRouteSync.py` file.
3. Open the existing folder:

   ```text
   Settings\Hardware\AutoRouteSync\
   ```

4. Replace the old `device_AutoRouteSync.py` with the new file.
5. Keep the virtual MIDI port running.
6. Keep the FL Studio MIDI input assignment unchanged.

If FL Studio does not recognize the replacement immediately, use **View > Script output > Reload** or restart FL Studio. You do not need to recreate the `AutoRouteSync` folder or configure the virtual MIDI port again.

## Troubleshooting

### The script is not listed in Controller type

Confirm that the script is located at:

```text
Settings\Hardware\AutoRouteSync\device_AutoRouteSync.py
```

Confirm that the filename begins with `device_` and ends with `.py`. Restart FL Studio after correcting the path.

### The script is listed but does nothing

Confirm all of the following:

- loopMIDI is running on Windows, or IAC Driver is online on macOS;
- the virtual MIDI input is enabled;
- `Auto-Route & Sync (user)` is selected in that input’s **Controller type** field;
- the script is inside the `AutoRouteSync` folder; and
- the `AutoRoute Virtual` port is still visible in FL Studio.

### The script output shows an error

Open **View > Script output** and review the first error shown after loading. Confirm that the script file was copied exactly as provided and was not renamed or saved with an additional `.txt` extension.

For temporary diagnostics, change `VERBOSE = False` to `VERBOSE = True` in the script. The script will then print routing and cleanup messages in the Script output window. Return it to `False` for normal silent operation.

## Reference links

- [FL Studio MIDI Scripting](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm)
- [FL Studio Controller/MIDI Settings](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/envsettings_midi.htm)
- [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
- [Apple Audio MIDI Setup and IAC Driver](https://support.apple.com/guide/audio-midi-setup/transfer-midi-information-between-apps-ams1013/mac)
